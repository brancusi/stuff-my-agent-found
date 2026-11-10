// The old clojure-radar.atd-ai.workers.dev address: send every request to the renamed site, same path and query.
// Old Clojure-only paths (/frontend/, /why-clojure/ ...) are then redirected again by the new site's _redirects.
export default {
  fetch(request) {
    const u = new URL(request.url);
    return Response.redirect('https://stuff-my-agent-found.atd-ai.workers.dev' + u.pathname + u.search, 301);
  },
};
