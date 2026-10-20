export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    url.hostname = 'generativelanguage.googleapis.com';
    const newHeaders = new Headers();
    for (const [key, value] of request.headers.entries()) {
      const lower = key.toLowerCase();
      if (!['host', 'cf-connecting-ip', 'cf-ipcountry', 'x-forwarded-for', 'x-real-ip'].includes(lower)) {
        newHeaders.set(key, value);
      }
    }
    const newRequest = new Request(url.toString(), {
      method: request.method,
      headers: newHeaders,
      body: request.body,
      redirect: 'follow'
    });
    return fetch(newRequest);
  }
};
