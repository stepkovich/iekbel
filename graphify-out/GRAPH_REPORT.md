# Graph Report - иэк.бел  (2026-11-17)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 258 nodes · 466 edges · 21 communities (10 shown, 11 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 6 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `92cd35a8`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Community 0
- Community 1
- Community 2
- Community 3
- Community 4
- Community 5
- Community 6
- Community 7
- Community 8
- Community 10
- Community 11
- Community 12
- Community 15

## God Nodes (most connected - your core abstractions)
1. `write_page()` - 15 edges
2. `build_product()` - 13 edges
3. `main()` - 13 edges
4. `build_home()` - 11 edges
5. `Handler` - 10 edges
6. `build_catalog()` - 10 edges
7. `DdpNode` - 9 edges
8. `breadcrumbs_html()` - 9 edges
9. `build_news()` - 9 edges
10. `build_category()` - 8 edges

## Surprising Connections (you probably didn't know these)
- `LocationInline` --uses--> `Location`  [INFERRED]
  catalog/admin.py → catalog/models.py
- `Command` --uses--> `News`  [INFERRED]
  catalog/management/commands/export_news.py → catalog/models.py
- `Command` --uses--> `DdpNode`  [INFERRED]
  catalog/management/commands/load_lk.py → catalog/models.py
- `Command` --uses--> `Product`  [INFERRED]
  catalog/management/commands/load_lk.py → catalog/models.py
- `Command` --uses--> `Order`  [INFERRED]
  catalog/management/commands/load_orders.py → catalog/models.py

## Import Cycles
- None detected.

## Communities (21 total, 11 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.09
Nodes (40): breadcrumbs_html(), breadcrumbs_ld(), build_404(), build_aux(), build_cart(), build_catalog(), build_category(), build_distributors() (+32 more)

### Community 1 - "Community 1"
Cohesion: 0.08
Nodes (12): Command, Command, make(), Command, DdpNode, Meta, News, Meta (+4 more)

### Community 2 - "Community 2"
Cohesion: 0.12
Nodes (12): main(), get(), load_env(), main(), download_image(), fetch_json(), get(), grab_images() (+4 more)

### Community 3 - "Community 3"
Cohesion: 0.09
Nodes (12): DdpNodeAdmin, DistributorAdmin, LocationAdmin, LocationInline, NewsAdmin, OrderAdmin, Media, ProductAdmin (+4 more)

### Community 4 - "Community 4"
Cohesion: 0.11
Nodes (7): main(), LinkCollector, main(), norm(), resolve(), extract_top_level_objects(), main()

### Community 5 - "Community 5"
Cohesion: 0.16
Nodes (7): Handler, items_for(), lk_bytes(), lk_json(), load_env(), load_residues(), main()

### Community 6 - "Community 6"
Cohesion: 0.22
Nodes (4): Migration, Migration, Migration, Migration

### Community 7 - "Community 7"
Cohesion: 0.53
Nodes (9): add(), bindSubmit(), bindTable(), esc(), load(), renderCart(), renderDistChoice(), save() (+1 more)

### Community 8 - "Community 8"
Cohesion: 0.51
Nodes (9): fetch(), handleDoc(), handleDocsMeta(), handleImage(), handleOrder(), handleStock(), json(), lkAuth() (+1 more)

### Community 10 - "Community 10"
Cohesion: 0.52
Nodes (6): esc2(), fmtQty(), loadDocs(), render(), stockTableHTML(), totalFor()

## Knowledge Gaps
- **11 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `DdpNode` connect `Community 1` to `Community 3`?**
  _High betweenness centrality (0.041) - this node is a cross-community bridge._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.09433962264150944 - nodes in this community are weakly interconnected._
- **Why does `News` connect `Community 1` to `Community 3`?**
  _High betweenness centrality (0.038) - this node is a cross-community bridge._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.07657657657657657 - nodes in this community are weakly interconnected._
- **Should `Community 2` be split into smaller, more focused modules?**
  _Cohesion score 0.12473118279569892 - nodes in this community are weakly interconnected._
- **Should `Community 3` be split into smaller, more focused modules?**
  _Cohesion score 0.08866995073891626 - nodes in this community are weakly interconnected._
- **Should `Community 4` be split into smaller, more focused modules?**
  _Cohesion score 0.10869565217391304 - nodes in this community are weakly interconnected._