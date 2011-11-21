#!/usr/bin/python

# Copyright (C) 2011 Linaro Limited
#
# Author: Paul Larson <paul.larson@linaro.org>
#
# This file is part of LAVA Dispatcher.
#
# LAVA Dispatcher is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# LAVA Dispatcher is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses>.

import json
import os
import shutil
import tarfile
import logging

from lava_dispatcher.actions import BaseAction
from lava_dispatcher.client import OperationFailed
from lava_dispatcher.utils import download
from tempfile import mkdtemp
import time
import xmlrpclib
import traceback

class SubmitResultAction(BaseAction):
    all_bundles = []
    def combine_bundles(self):
        if not self.all_bundles:
            return {
                     "test_runs": [],
                     "format": "Dashboard Bundle Format 1.2"
                   }
        main_bundle = self.all_bundles.pop(0)
        test_runs = main_bundle['test_runs']
        for bundle in self.all_bundles:
            test_runs += bundle['test_runs']
        return main_bundle

    def submit_combine_bundles(self, status='pass', err_msg='', server=None, stream=None):
        dashboard = _get_dashboard(server)
        main_bundle = self.combine_bundles()
        self.context.test_data.add_seriallog(
            self.context.client.get_seriallog())
        # add gather_results result
        self.context.test_data.add_result('gather_results', status, err_msg)
        main_bundle['test_runs'].append(self.context.test_data.get_test_run())
        for test_run in main_bundle['test_runs']:
            attributes = test_run.get('attributes', {})
            attributes.update(self.context.test_data.get_metadata())
            test_run['attributes'] = attributes
        json_bundle = json.dumps(main_bundle)
        job_name = self.context.job_data.get('job_name', "LAVA Results")
        try:
            print >> self.context.oob_file, 'dashboard-put-result:', \
                  dashboard.put_ex(json_bundle, job_name, stream)
        except xmlrpclib.Fault, err:
            logging.warning("xmlrpclib.Fault occurred")
            logging.warning("Fault code: %d" % err.faultCode)
            logging.warning("Fault string: %s" % err.faultString)

class cmd_submit_results_on_host(SubmitResultAction):
    def run(self, server, stream):
        #Upload bundle files to dashboard
        logging.info("Executing submit_results_on_host command")
        bundlename_list = []
        status = 'pass'
        err_msg = ''
        try:
            bundle_list = os.listdir(self.context.host_result_dir)
            for bundle_name in bundle_list:
                bundle = "%s/%s" % (self.context.host_result_dir, bundle_name)
                bundlename_list.append(bundle)
                f = open(bundle)
                content = f.read()
                f.close()
                self.all_bundles.append(json.loads(content))
        except:
            print traceback.format_exc()
            status = 'fail'
            err_msg = err_msg + " Some test case result appending failed."

        self.submit_combine_bundles(status, err_msg, server, stream)

        for bundle in bundlename_list:
            os.remove(bundle)
        shutil.rmtree(self.context.host_result_dir)
        if status == 'fail':
            raise OperationFailed(err_msg)


class cmd_submit_results(SubmitResultAction):

    def _get_result_tarball(self, result_disk):
        with self.client._master_session() as session:

            session.run('mkdir -p /mnt/root')
            session.run(
                'mount /dev/disk/by-label/%s /mnt/root' % result_disk)
            # Clean results directory on master image
            session.run(
                'rm -rf /tmp/lava_results.tgz /tmp/%s' % self.context.lava_result_dir)
            session.run('mkdir -p /tmp/%s' % self.context.lava_result_dir)
            session.run(
                'cp /mnt/root/%s/*.bundle /tmp/%s' % (self.context.lava_result_dir,
                    self.context.lava_result_dir))
            # Clean result bundle on test image
            session.run(
                'rm -f /mnt/root/%s/*.bundle' % (self.context.lava_result_dir))
            session.run('umount /mnt/root')

            # Create tarball of all results
            logging.info("Creating lava results tarball")
            session.run('cd /tmp')
            session.run(
                'tar czf /tmp/lava_results.tgz -C /tmp/%s .' % self.context.lava_result_dir)

            # start gather_result job, status
            err_msg = ''
            master_ip = session.get_master_ip()
            if not master_ip:
                err_msg = err_msg + "Getting master image IP address failed, \
    no test case result retrived."
                logging.warning(err_msg)
                return 'fail', err_msg, None
            # Set 80 as server port
            session.run('python -m SimpleHTTPServer 80 &> /dev/null &')
            time.sleep(3)

            result_tarball = "http://%s/lava_results.tgz" % master_ip
            tarball_dir = mkdtemp(dir=self.context.lava_image_tmpdir)
            os.chmod(tarball_dir, 0755)

            # download test result with a retry mechanism
            # set retry timeout to 2mins
            logging.info("About to download the result tarball to host")
            now = time.time()
            timeout = 120
            tries = 0
            try:
                while time.time() < now + timeout:
                    try:
                        result_path = download(
                            result_tarball, tarball_dir,
                            verbose_failure=tries==0)
                    except RuntimeError:
                        tries += 1
                        if time.time() >= now + timeout:
                            logging.exception("download failed")
                            raise
            except:
                logging.warning(traceback.format_exc())
                err_msg = err_msg + " Can't retrieve test case results."
                logging.warning(err_msg)
                return 'fail', err_msg, None

            session.run('kill %1')
            session.run('')

            return 'pass', None, result_path

    def run(self, server, stream, result_disk="testrootfs"):
        """Submit test results to a lava-dashboard server
        :param server: URL of the lava-dashboard server RPC endpoint
        :param stream: Stream on the lava-dashboard server to save the result to
        """

        status, err_msg, result_path = self._get_result_tarball(result_disk)
        if result_path is not None:
            try:
                tar = tarfile.open(result_path)
                for tarinfo in tar:
                    if os.path.splitext(tarinfo.name)[1] == ".bundle":
                        f = tar.extractfile(tarinfo)
                        content = f.read()
                        f.close()
                        self.all_bundles.append(json.loads(content))
                tar.close()
            except:
                logging.warning(traceback.format_exc())
                status = 'fail'
                err_msg = err_msg + " Some test case result appending failed."
                logging.warning(err_msg)
            finally:
                shutil.rmtree(os.path.dirname(result_path))

        self.submit_combine_bundles(status, err_msg, server, stream)
        if status == 'fail':
            raise OperationFailed(err_msg)

#util function, see if it needs to be part of utils.py
def _get_dashboard(server):
    if not server.endswith("/"):
        server = ''.join([server, "/"])

    #add backward compatible for 'dashboard/'-end URL
    #Fix it: it's going to be deleted after transition
    if server.endswith("dashboard/"):
        server = ''.join([server, "xml-rpc/"])
        logging.warn("Please use whole endpoint URL not just end with 'dashboard/', 'xml-rpc/' is added automatically now!!!")

    srv = xmlrpclib.ServerProxy(server, allow_none=True, use_datetime=True)
    if server.endswith("xml-rpc/"):
        logging.warn("Please use RPC2 endpoint instead, xml-rpc is deprecated!!!")
        dashboard = srv
    elif server.endswith("RPC2/"):
        #include lava-server/RPC2/
        dashboard = srv.dashboard
    else:
        logging.warn("The url seems not RPC2 or xml-rpc endpoints, please make sure it's a valid one!!!")
        dashboard = srv.dashboard

    logging.info("server RPC endpoint URL: %s" % server)
    return dashboard

