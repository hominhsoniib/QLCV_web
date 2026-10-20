export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    url.hostname = 'generativelanguage.googleapis.com';
    const newHeaders = new Headers(request.headers);
    newHeaders.delete('host');
    const newRequest = new Request(url.toString(), {
      method: request.method,
      headers: newHeaders,
      body: request.body,
      redirect: 'follow'
    });
    return fetch(newRequest);
  }
};
