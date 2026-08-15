const canonicalOverview = "https://abhilashkr.com/#ai-human-workspace";
const noindexPolicy = "noindex, nofollow, noarchive, nosnippet, noimageindex";

function canonicalRedirect() {
  return new Response(null, {
    status: 308,
    headers: {
      Location: canonicalOverview,
      "X-Robots-Tag": noindexPolicy,
    },
  });
}

export function GET() {
  return canonicalRedirect();
}

export function HEAD() {
  return canonicalRedirect();
}
