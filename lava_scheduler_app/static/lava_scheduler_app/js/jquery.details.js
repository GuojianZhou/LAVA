/*! http://mths.be/details v0.0.1 by @mathias */
(function (a, $) {
    var c = $.fn,
        b, d = (function (i) {
            var g = i.createElement("details"),
                f, e, h;
            if (!("open" in g)) {
                return false
            }
            e = i.body || (function () {
                var j = i.documentElement;
                f = true;
                return j.insertBefore(i.createElement("body"), j.firstElementChild || j.firstChild)
            }());
            g.innerHTML = "<summary>a</summary>b";
            g.style.display = "block";
            e.appendChild(g);
            h = g.offsetHeight;
            g.open = true;
            h = h != g.offsetHeight;
            e.removeChild(g);
            if (f) {
                e.parentNode.removeChild(e)
            }
            return h
        }(a));
    /*! http://mths.be/noselect v1.0.2 by @mathias */
    c.noSelect = function () {
        var e = "none";
        return this.bind("selectstart dragstart mousedown", function () {
            return false
        }).css({
            MozUserSelect: e,
            WebkitUserSelect: e,
            userSelect: e
        })
    };
    if (d) {
        b = c.details = function () {
            return this
        };
        b.support = d
    } else {
        b = c.details = function () {
            return this.each(function () {
                var e = $(this),
                    h = $("summary", e),
                    g = e.children(":not(summary)"),
                    i = e.contents(":not(summary)"),
                    f = this.getAttribute("open");
                if (!h.length) {
                    h = $(a.createElement("summary")).text("Details").prependTo(e)
                }
                if (g.length != i.length) {
                    i.filter(function () {
                        return (this.nodeType === 3) && (/[^ \t\n\f\r]/.test(this.data))
                    }).wrap("<span>");
                    g = e.children(":not(summary)")
                }
                if (typeof f == "string" || (typeof f == "boolean" && f)) {
                    e.addClass("open");
                    g.show()
                } else {
                    g.hide()
                }
                h.noSelect().attr("tabIndex", 0).click(function () {
                    h.focus();
                    typeof e.attr("open") != "undefined" ? e.removeAttr("open") : e.attr("open", "open");
                    g.toggle(0);
                    e.toggleClass("open")
                }).keyup(function (j) {
                    if (13 === j.keyCode || 32 === j.keyCode) {
                        if (!($.browser.opera && 13 === j.keyCode)) {
                            j.preventDefault();
                            h.click()
                        }
                    }
                })
            })
        };
        b.support = d
    }
}(document, jQuery));
