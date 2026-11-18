# Graph Report - иэк.бел  (2026-11-18)

## Corpus Check
- 43 files · ~57,074 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 14 file(s) not represented in the graph (top: .gz 4, .css 3, .log 3)

## Summary
- 315 nodes · 564 edges · 30 communities (15 shown, 15 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 8 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `0c70d691`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- build.py
- admin.py
- import_lk.py
- DdpNode
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
- export_news.py
- models.py
- django_db
- Location
- Distributor

## God Nodes (most connected - your core abstractions)
1. `write_page()` - 15 edges
2. `build_product()` - 13 edges
3. `main()` - 13 edges
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
- `Command` --uses--> `Order`  [INFERRED]
  catalog/management/commands/load_orders.py → catalog/models.py
- `Command` --uses--> `DdpNode`  [INFERRED]
  catalog/management/commands/load_lk.py → catalog/models.py
- `Command` --uses--> `Product`  [INFERRED]
  catalog/management/commands/load_lk.py → catalog/models.py

## Import Cycles
- None detected.

## Communities (30 total, 15 thin omitted)

### Community 0 - "build.py"
Cohesion: 0.09
Nodes (40): breadcrumbs_html(), breadcrumbs_ld(), build_404(), build_aux(), build_cart(), build_catalog(), build_category(), build_distributors() (+32 more)

### Community 1 - "admin.py"
Cohesion: 0.20
Nodes (7): DdpNodeAdmin, DistributorAdmin, LocationAdmin, NewsAdmin, OrderAdmin, Media, ProductAdmin

### Community 2 - "import_lk.py"
Cohesion: 0.11
Nodes (12): main(), get(), load_env(), main(), download_image(), fetch_json(), get(), grab_images() (+4 more)

### Community 3 - "DdpNode"
Cohesion: 0.24
Nodes (6): Command, make(), DdpNode, Meta, Product, Meta

### Community 4 - "check_links.py"
Cohesion: 0.14
Nodes (6): LinkCollector, main(), norm(), resolve(), extract_top_level_objects(), main()

### Community 5 - "devserver.py"
Cohesion: 0.16
Nodes (7): Handler, items_for(), lk_bytes(), lk_json(), load_env(), load_residues(), main()

### Community 7 - "cart.js"
Cohesion: 0.53
Nodes (9): add(), bindSubmit(), bindTable(), esc(), load(), renderCart(), renderDistChoice(), save() (+1 more)

### Community 8 - "worker.js"
Cohesion: 0.51
Nodes (9): fetch(), handleDoc(), handleDocsMeta(), handleImage(), handleOrder(), handleStock(), json(), lkAuth() (+1 more)

### Community 9 - "run.py"
Cohesion: 0.12
Nodes (12): main(), build_if_needed(), ensure_data(), ensure_db(), ensure_python(), have_env_keys(), main(), newest_mtime() (+4 more)

### Community 10 - "live.js"
Cohesion: 0.52
Nodes (6): esc2(), fmtQty(), loadDocs(), render(), stockTableHTML(), totalFor()

### Community 22 - "files"
Cohesion: 0.14
Nodes (13): backup_id, datetime, files, catalog.json, distributors.json, etim.db.gz, import_partial.json.gz, lk-cats.tar.gz (+5 more)

### Community 23 - "export_news.py"
Cohesion: 0.18
Nodes (3): Command, News, Meta

### Community 24 - "models.py"
Cohesion: 0.24
Nodes (3): Command, Order, Meta

### Community 25 - "django_db"
Cohesion: 0.22
Nodes (4): Migration, Migration, Migration, Migration

### Community 26 - "Location"
Cohesion: 0.40
Nodes (3): LocationInline, Location, Meta

## Knowledge Gaps
- **15 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `DdpNode` connect `DdpNode` to `models.py`, `admin.py`, `import_lk.py`?**
  _High betweenness centrality (0.033) - this node is a cross-community bridge._
- **Should `build.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09433962264150944 - nodes in this community are weakly interconnected._
- **Should `import_lk.py` be split into smaller, more focused modules?**
  _Cohesion score 0.1092436974789916 - nodes in this community are weakly interconnected._
- **Should `check_links.py` be split into smaller, more focused modules?**
  _Cohesion score 0.14035087719298245 - nodes in this community are weakly interconnected._
- **Should `run.py` be split into smaller, more focused modules?**
  _Cohesion score 0.11954022988505747 - nodes in this community are weakly interconnected._
- **Should `backup.py` be split into smaller, more focused modules?**
  _Cohesion score 0.13043478260869565 - nodes in this community are weakly interconnected._
- **Should `files` be split into smaller, more focused modules?**
  _Cohesion score 0.14285714285714285 - nodes in this community are weakly interconnected._