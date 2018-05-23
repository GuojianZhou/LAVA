.. _deploy_action:

Deploy Action Reference
#######################

In general, the deployments do not modify the downloaded files. Where the LAVA
scripts and test definitions need to be added, these are first prepared as a
standalone tarball. Exceptions are described where relevant in each section.

Deploy action roles
*******************

* Download files required by the job to the dispatcher, decompressing only if
  requested.

* Prepare a LAVA overlay tarball containing the test definitions and LAVA API
  scripts, only if a :ref:`test_action` action is defined.

* Depending on the deployment, apply the LAVA overlay tarball to the
  deployment.

* Deploy does not support :ref:`repeat <repeats>` blocks but does support
  :ref:`failure_retry`.

.. _deploy_parameters:

Required parameters
*******************

Every deployment **must** specify a ``to`` parameter. This value is then used
to select the appropriate Strategy class for the deployment which, in turn,
will require other parameters to provide the data on how to deploy to the
requested location. Additionally, all the required parameters are marked with
a *****

.. # comment - WARNING: respect the capitalisation (or lack of such) in all the
   following sections as these are intended to exactly match the examples.
   Also, ignore the repetition - this is a *reference* guide like the glossary,
   it is not meant to be readable from top to bottom. Each section needs to
   standalone as a complete reference. Refer to other sections in other pages
   but avoid referring to other links in this document except when a direct
   relationship already exists through inheritance. There is a need for some
   custom CSS here, possibly using .. container:: RST syntax to assist with the
   sub-division of elements, possibly indenting.
   Also, watch for nesting levels. The links to sections are indented by
   **meaning**, even if the actual element is at a different level. This is to
   keep the guide consistent.
   Keep the docs for each element short and refer to the main body of docs for
   explanations. Ensure all information on options and possible values is in the
   reference guide.

Parameter List
**************

.. contents::
   :backlinks: top

.. include:: actions-deploy-to-fastboot.rsti
.. include:: actions-deploy-to-isoinstaller.rsti
.. include:: actions-deploy-to-lxc.rsti
.. include:: actions-deploy-to-sata.rsti
.. include:: actions-deploy-to-ssh.rsti
.. include:: actions-deploy-to-tftp.rsti
.. include:: actions-deploy-to-nbd.rsti
.. include:: actions-deploy-to-usb.rsti
.. include:: actions-deploy-to-download.rsti
.. include:: actions-deploy-to-recovery.rsti

.. index:: deploy os

.. _deploy_os:

os *
****

The operating system of the image **must** be specified so that the LAVA
scripts can install packages and identify other defaults in the deployment
data.

* **Not all deployment methods support all types of operating system.**
* **Not all devices can support all operating systems.**

.. topic:: Allowed values

 * ``android``
 * ``ubuntu``
 * ``debian``
 * ``lede``
 * ``fedora``
 * ``centos``
 * ``debian_installer``
 * ``centos_installer``
 * ``oe``
