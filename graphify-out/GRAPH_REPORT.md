# Graph Report - иэк.бел  (2026-11-23)

## Corpus Check
- 41 files · ~79,808 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 14 file(s) not represented in the graph (top: .css 3, .gz 3, (none) 2)

## Summary
- 330 nodes · 591 edges · 25 communities (14 shown, 11 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 11 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e8db8d97`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- build.py
- admin.py
- import_lk.py
- suggest.js
- check_links.py
- devserver.py
- cart.js
- worker.js
- run.py
- live.js
- apps.py
- search.js
- dev.sh
- backup.py
- files
- django_db
- models.py

## God Nodes (most connected - your core abstractions)
1. `main()` - 17 edges
2. `write_page()` - 15 edges
3. `build_product()` - 13 edges
4. `build_home()` - 11 edges
5. `BackupManager` - 11 edges
6. `build_catalog()` - 10 edges
7. `Handler` - 10 edges
8. `breadcrumbs_html()` - 9 edges
9. `build_news()` - 9 edges
10. `DdpNode` - 9 edges

## Surprising Connections (you probably didn't know these)
- `LocationInline` --uses--> `Location`  [INFERRED]
  catalog/admin.py → catalog/models.py
- `main()` --calls--> `slugify()`  [EXTRACTED]
  tools/import_lk.py → tools/build.py
- `Command` --uses--> `News`  [INFERRED]
  catalog/management/commands/export_news.py → catalog/models.py
- `Command` --uses--> `DdpNode`  [INFERRED]
  catalog/management/commands/load_lk.py → catalog/models.py
- `Command` --uses--> `Product`  [INFERRED]
  catalog/management/commands/load_lk.py → catalog/models.py

## Import Cycles
- None detected.

## Communities (25 total, 11 thin omitted)

### Community 0 - "build.py"
Cohesion: 0.08
Nodes (44): breadcrumbs_html(), breadcrumbs_ld(), build_404(), build_aux(), build_cart(), build_catalog(), build_category(), build_distributors() (+36 more)

### Community 1 - "admin.py"
Cohesion: 0.10
Nodes (10): DdpNodeAdmin, DistributorAdmin, LocationAdmin, LocationInline, NewsAdmin, OrderAdmin, Media, ProductAdmin (+2 more)

### Community 2 - "import_lk.py"
Cohesion: 0.11
Nodes (12): main(), get(), load_env(), main(), download_image(), fetch_json(), get(), grab_images() (+4 more)

### Community 3 - "suggest.js"
Cohesion: 0.70
Nodes (4): ensureIndex(), norm(), render(), search()

### Community 4 - "check_links.py"
Cohesion: 0.14
Nodes (6): LinkCollector, main(), norm(), resolve(), extract_top_level_objects(), main()

### Community 5 - "devserver.py"
Cohesion: 0.16
Nodes (7): Handler, items_for(), lk_bytes(), lk_json(), load_env(), load_residues(), main()

### Community 7 - "cart.js"
Cohesion: 0.41
Nodes (11): add(), bindSubmit(), bindTable(), esc(), load(), renderCart(), renderDistChoice(), renderPartners() (+3 more)

### Community 8 - "worker.js"
Cohesion: 0.51
Nodes (9): fetch(), handleDoc(), handleDocsMeta(), handleImage(), handleOrder(), handleStock(), json(), lkAuth() (+1 more)

### Community 9 - "run.py"
Cohesion: 0.12
Nodes (12): main(), build_if_needed(), ensure_data(), ensure_db(), ensure_python(), have_env_keys(), main(), newest_mtime() (+4 more)

### Community 10 - "live.js"
Cohesion: 0.52
Nodes (6): esc2(), fmtQty(), loadDocs(), render(), stockTableHTML(), totalFor()

### Community 12 - "search.js"
Cohesion: 0.83
Nodes (3): esc(), norm(), render()

### Community 22 - "files"
Cohesion: 0.14
Nodes (13): backup_id, datetime, files, catalog.json, distributors.json, etim.db.gz, import_partial.json.gz, lk-cats.tar.gz (+5 more)

### Community 25 - "django_db"
Cohesion: 0.22
Nodes (4): Migration, Migration, Migration, Migration

### Community 29 - "models.py"
Cohesion: 0.07
Nodes (14): Command, Command, make(), Command, DdpNode, Meta, Distributor, Meta (+6 more)

## Knowledge Gaps
- **11 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `DdpNode` connect `models.py` to `admin.py`?**
  _High betweenness centrality (0.032) - this node is a cross-community bridge._
- **Should `build.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08248587570621468 - nodes in this community are weakly interconnected._
- **Should `admin.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09686609686609686 - nodes in this community are weakly interconnected._
- **Should `import_lk.py` be split into smaller, more focused modules?**
  _Cohesion score 0.11290322580645161 - nodes in this community are weakly interconnected._
- **Should `check_links.py` be split into smaller, more focused modules?**
  _Cohesion score 0.14035087719298245 - nodes in this community are weakly interconnected._
- **Should `run.py` be split into smaller, more focused modules?**
  _Cohesion score 0.11612903225806452 - nodes in this community are weakly interconnected._
- **Should `backup.py` be split into smaller, more focused modules?**
  _Cohesion score 0.13043478260869565 - nodes in this community are weakly interconnected._