import { readdirSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
import ts from 'typescript';
import { describe, expect, it } from 'vitest';

function tsxFiles(directory: string): string[] {
  return readdirSync(directory, { withFileTypes: true }).flatMap((entry) => {
    const path = join(directory, entry.name);
    if (entry.isDirectory()) {
      if (path.endsWith(join('components', 'ui'))) return [];
      return tsxFiles(path);
    }
    return entry.isFile() && entry.name.endsWith('.tsx') ? [path] : [];
  });
}

describe('application button contract', () => {
  it('gives every application button an id and an explicit action', () => {
    const violations: string[] = [];
    const files = [
      ...tsxFiles(join(process.cwd(), 'app')),
      ...tsxFiles(join(process.cwd(), 'components')),
    ];

    for (const file of files) {
      const source = ts.createSourceFile(
        file,
        readFileSync(file, 'utf8'),
        ts.ScriptTarget.Latest,
        true,
        ts.ScriptKind.TSX,
      );
      const visit = (node: ts.Node) => {
        if (ts.isJsxOpeningElement(node) || ts.isJsxSelfClosingElement(node)) {
          const tag = node.tagName.getText(source);
          if (tag === 'Button' || tag === 'button') {
            const attributes = node.attributes.properties
              .filter(ts.isJsxAttribute)
              .map((attribute) => attribute.name.getText(source));
            const line = source.getLineAndCharacterOfPosition(
              node.getStart(source),
            ).line;
            if (!attributes.includes('id'))
              violations.push(`${file}:${line + 1} thiếu id`);
            if (
              !attributes.some((attribute) =>
                ['onClick', 'type', 'formAction'].includes(attribute),
              )
            )
              violations.push(`${file}:${line + 1} thiếu hành vi`);
          }
        }
        ts.forEachChild(node, visit);
      };
      visit(source);
    }

    expect(violations).toEqual([]);
  });
});
