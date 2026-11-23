import { DurableObject } from "cloudflare:workers";

export class PatchCounter extends DurableObject {
  total() {
    return this.ctx.storage.kv.get("count") ?? 0;
  }

  increment() {
    const count = this.total() + 1;
    this.ctx.storage.kv.put("count", count);
    return count;
  }
}

export default {
  async fetch(request, env) {
    if (new URL(request.url).pathname !== "/patches") {
      return new Response(null, { status: 404 });
    }

    const { method } = request;
    if (method !== "GET" && method !== "POST") {
      return new Response(null, { status: 405, headers: { Allow: "GET, POST" } });
    }
    if (method === "POST" && request.headers.get("Origin") !== env.ALLOWED_ORIGIN) {
      return new Response(null, { status: 403 });
    }

    const counter = env.PATCH_COUNTER.getByName("total");
    const count = method === "POST" ? await counter.increment() : await counter.total();
    return Response.json({ count }, {
      headers: { "Access-Control-Allow-Origin": "*", "Cache-Control": "no-store" },
    });
  },
};
