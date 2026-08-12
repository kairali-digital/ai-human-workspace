import manifest from "../content/download-manifest.json";
import type { DownloadGroup as DownloadGroupType } from "../content/site-data";

const downloadSizes = new Map(manifest.files.map((file) => [file.name, file.size]));

function readableBytes(bytes: number) {
  if (bytes >= 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  if (bytes >= 1024) return `${Math.round(bytes / 1024)} KB`;
  return `${bytes} B`;
}

export function DownloadGroup({ group }: { group: DownloadGroupType }) {
  return (
    <article className={group.featured ? "download-group download-group-featured" : "download-group"}>
      <div className="download-heading">
        <h3>{group.title}</h3>
        <p>{group.description}</p>
      </div>
      <div className="download-items">
        {group.items.map((item) => (
          <a
            className="download-item"
            href={`/downloads/${encodeURIComponent(item.file)}`}
            key={item.file}
            download
          >
            <span>
              <strong>{item.label}</strong>
              <small>{item.description}</small>
            </span>
            <span className="download-meta">
              {item.format}
              {downloadSizes.has(item.file) ? ` / ${readableBytes(downloadSizes.get(item.file) ?? 0)}` : ""}
            </span>
          </a>
        ))}
      </div>
    </article>
  );
}
