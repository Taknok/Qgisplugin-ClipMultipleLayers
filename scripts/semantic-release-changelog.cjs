const fs = require("node:fs");
const path = require("node:path");

module.exports = {
  prepare(_pluginConfig, context) {
    const changelogPath = path.resolve("CHANGELOG.md");
    const current = fs.existsSync(changelogPath)
      ? fs.readFileSync(changelogPath, "utf8")
      : "# Changelog\n\n";
    const heading = `## [${context.nextRelease.version}] - ${new Date()
      .toISOString()
      .slice(0, 10)}`;

    const versionPrefix = `## [${context.nextRelease.version}] - `;
    if (current.split(/\r?\n/).some((line) => line.startsWith(versionPrefix))) {
      throw new Error(`Changelog already contains ${context.nextRelease.version}`);
    }

    const lines = String(context.nextRelease.notes || "")
      .trim()
      .split(/\r?\n/);
    if (lines[0] && /^#\s/.test(lines[0])) {
      lines.shift();
    }
    const notes = lines
      .map((line) => line.replace(/^(#{1,6})\s+(.+)$/, "**$2**"))
      .join("\n")
      .trim();
    const title = current.match(/^# Changelog\s*\r?\n/i);
    const prefix = title ? title[0].trimEnd() : "# Changelog";
    const previousEntries = title
      ? current.slice(title[0].length).trim()
      : current.trim();
    const entry = [heading, notes].filter(Boolean).join("\n\n");
    const updated = [prefix, entry, previousEntries]
      .filter(Boolean)
      .join("\n\n");

    fs.writeFileSync(changelogPath, `${updated}\n`);
  },
};
