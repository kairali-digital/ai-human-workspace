import type { MetadataRoute } from "next";

const SITE_URL = "https://kairali-ai-method.vercel.app";

export default function sitemap(): MetadataRoute.Sitemap {
  return [{ url: SITE_URL }];
}
