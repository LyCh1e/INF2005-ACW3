/* Shared nav behaviour: reflect signed-in state and provide a log out.
   State is the per-session flag set by login.html after a successful
   digest sign-in. Loaded on every page that has the top nav. */
(function () {
  "use strict";

  var signedIn = false, user = "";
  try {
    signedIn = sessionStorage.getItem("fieldstone.loggedIn") === "1";
    user = sessionStorage.getItem("fieldstone.user") || "";
  } catch (e) { /* storage blocked - treat as signed out */ }

  function build() {
    var cta = document.querySelector(".topnav .nav-cta");
    if (!cta || !signedIn) return;              // signed out: leave "Sign in" as-is
    var nav = cta.parentNode;

    // one-time styles for the signed-in indicator
    if (!document.getElementById("navjs-style")) {
      var st = document.createElement("style");
      st.id = "navjs-style";
      st.textContent =
        ".nav-user{display:inline-flex;align-items:center;gap:7px;color:#cdd8cf;" +
        "font-size:.9em;padding:0 6px 0 4px;}" +
        ".nav-user-dot{width:7px;height:7px;border-radius:50%;background:#7fae63;" +
        "box-shadow:0 0 6px rgba(127,174,99,.85);display:inline-block;}";
      document.head.appendChild(st);
    }

    // "Signed in · user" indicator
    var chip = document.createElement("span");
    chip.className = "nav-user";
    chip.appendChild(Object.assign(document.createElement("span"), { className: "nav-user-dot" }));
    chip.appendChild(document.createTextNode(user ? "Signed in as " + user : "Signed in"));

    // Log out button (reuses the existing .nav-cta styling)
    var out = document.createElement("a");
    out.className = "nav-cta";
    out.href = "#";
    out.textContent = "Log out";
    out.title = "Clears this session. Closing the browser also signs you out.";
    out.addEventListener("click", logout);

    nav.replaceChild(out, cta);
    nav.insertBefore(chip, out);
  }

  function logout(ev) {
    ev.preventDefault();
    try {
      sessionStorage.removeItem("fieldstone.loggedIn");
      sessionStorage.removeItem("fieldstone.user");
    } catch (e) {}
    // Best-effort: replace the browser's cached digest credentials with bad
    // ones so /dav/ challenges again. Not guaranteed across all browsers;
    // closing the browser is the sure way to drop cached credentials.
    try {
      var x = new XMLHttpRequest();
      x.open("GET", "/dav/", true, "loggedout", "loggedout");
      x.onloadend = function () { window.location.href = "/"; };
      x.send();
    } catch (e) {
      window.location.href = "/";
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", build);
  } else {
    build();
  }
})();
