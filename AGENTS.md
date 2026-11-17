## graphify

В проекте построен knowledge graph: `graphify-out/` (graphify 0.9.112, локальный AST, без LLM).

Правила для агентов (ZCode/PyCharm и любые другие):
- Ориентация по коду: сначала `graphify-out/wiki/index.md` и `graphify-out/GRAPH_REPORT.md`,
  точечные вопросы — через CLI: `graphify query "…"`, `graphify path A B`, `graphify explain X`,
  `graphify affected X` (кто сломается при изменении X), `graphify god-nodes`.
- После правки python/js-кода: `graphify update .` (AST-only, без API-ключей, секунды).
- После крупных рефакторов: полный ребилд `graphify . --code-only` + wiki через python-API
  (см. graphify-out/wiki/).
- Контентные тексты (новости, описания) в граф не входят — он про код и связи.

Команды обновления контура (win/linux):
  ~/mmenv/bin/graphify update .        # инкрементально
  ~/mmenv/bin/graphify . --code-only   # полный ребилд
