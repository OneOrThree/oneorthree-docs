import { sections, site } from "@root/site.config";
import { getDocs } from "@/lib/content";
import { getDiagrams } from "@/lib/diagrams";

/**
 * llms.txt — a plain-text map of the site for language models, carried over
 * from both clones. Generated from `content/`, so it cannot go stale.
 */
export const dynamic = "force-static";

export function GET(): Response {
  const lines: string[] = [
    `# ${site.name}`,
    "",
    `> ${site.description}`,
    "",
  ];

  for (const section of sections) {
    lines.push(`## ${section.title}`, "", section.description, "");

    if (section.kind === "diagrams") {
      for (const diagram of getDiagrams()) {
        lines.push(
          `- [${diagram.title}](${site.origin}/diagrams/${diagram.id})` +
            (diagram.summary ? `: ${diagram.summary}` : ""),
        );
      }
    } else {
      for (const doc of getDocs(section.slug)) {
        const recordLabel = doc.recordType === "current" ? "현재 안내" : doc.recordType === "decision" ? "결정 기록 · 적용 범위 확인" : "당시 기록";
        const meta = [recordLabel, doc.status, doc.date].filter(Boolean).join(" · ");
        lines.push(
          `- [${doc.title}](${site.origin}${doc.href})` +
            (meta ? ` (${meta})` : "") +
            (doc.summary ? `: ${doc.summary}` : ""),
        );
      }
    }

    lines.push("");
  }

  return new Response(lines.join("\n"), {
    headers: { "content-type": "text/plain; charset=utf-8" },
  });
}
