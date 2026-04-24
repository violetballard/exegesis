# Post-adfa Retrieval Commit Accounting

- Prior reviewed head: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Pre-fix branch tip restamped by this packet pass: `35c7fe709107d4d26567a29e0529f8a104d18cdb`
- Post-`adfa8cdadd` runtime/test commits: `265`
- Post-`adfa8cdadd` metadata-only commits: `680`

## Runtime/Test Commits

- `2188b405f32d8977703da90b4b560e53b99142bd` fix(retrieval): align review packet metadata
  Files: `.codex/kickoff_packets/feat-retrieval-fts.md`, `.codex/lane_meta/feat-retrieval-fts.json`, `THREAD_PACKET.md`, `codex_packet_handoff/tools/planner.py`, `tests/unit/test_packet_planner.py`
- `194612f4d9bfa121484adaf25468dd22e26eabc5` fix(retrieval): separate metadata packet head from reviewed range
  Files: `.codex/lane_meta/feat-retrieval-fts.json`, `THREAD_PACKET.md`, `codex_packet_handoff/tools/planner.py`, `tests/unit/test_packet_planner.py`
- `5420c99a7729e2263160e4c65f3fb10b06f91f7f` fix(retrieval): clarify packet head lineage
  Files: `.codex/kickoff_packets/feat-retrieval-fts.md`, `.codex/lane_meta/feat-retrieval-fts.json`, `THREAD_PACKET.md`, `codex_packet_handoff/tools/planner.py`, `tests/unit/test_packet_planner.py`
- `0d21c11e2a3866b6944c98240a2fe8f0678551bf` feat: harden fts retrieval snapshots
  Files: `src/qual/engine/retrieval/embeddings_strategy.py`, `src/qual/engine/retrieval/fts_strategy.py`, `src/qual/engine/retrieval/interface.py`, `src/qual/engine/retrieval/pageindex_strategy.py`, `src/qual/engine/retrieval/payload.py`, `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`
- `226121095e4d889d79feabfb9966a84b756d5753` Backfill sparse retrieval source bundles
  Files: `src/qual/engine/retrieval/payload.py`, `tests/unit/test_unified_retrieval.py`
- `2b32538cdaf7e00726607fbe11c6957de0d7d739` Harden retrieval citation payload backfills
  Files: `src/qual/engine/retrieval/payload.py`, `tests/unit/test_unified_retrieval.py`
- `73ad9229b1a6c1d47a90a52f6a92dbc5fab0f64f` retrieval: honor section hints in fts ranking
  Files: `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`
- `91899af618c0d62461c1512db42f4466b962beb2` feat-retrieval-fts: preserve title hints on excerpt lookup
  Files: `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`
- `712714c24f92cdfe43f21127c2de1d4ea0bd2599` Normalize retrieval date range ordering
  Files: `src/qual/retrieval/service.py`
- `3048d5175c1371e9e89d71de55b440c35bfee5ce` Normalize retrieval query snapshots
  Files: `src/qual/engine/retrieval/payload.py`, `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`
- `fb2f0445b9c00a072a96acce9d6e4c3f6b585ddf` feat-retrieval-fts: preserve sparse citation provenance
  Files: `src/qual/engine/retrieval/payload.py`
- `380748890f6b79e9f5eb0e6842018d7d36a4b492` Improve FTS cache key canonicalization
  Files: `src/qual/engine/retrieval/fts_strategy.py`, `tests/unit/test_unified_retrieval.py`
- `b9ead9185eeca0d90e3761508d597ede93477d54` feat(retrieval): enrich FTS evidence context
  Files: `src/qual/engine/retrieval/payload.py`, `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`
- `c558a819bde1a4245bf73a38f968929b0c90d93d` Normalize retrieval constraint booleans
  Files: `src/qual/engine/retrieval/__init__.py`
- `d75472a6ba2a6d2b543e1e9c928f54711e42ccb1` Fix FTS cache scope normalization
  Files: `src/qual/engine/retrieval/fts_strategy.py`, `tests/unit/test_unified_retrieval.py`
- `f54fdf6c19da7b9b22a4377e2eacdad600c2e8e3` Honor excerpt lookup confidentiality profiles
  Files: `src/qual/retrieval/__init__.py`, `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`
- `daeb0916ad0474ae1bc8b25235f0e9f8130e8e85` Harden retrieval excerpt provenance normalization
  Files: `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`
- `8689af98b089a0d3c061e57f2b0c5e3ab72a5177` Normalize canonical retrieval query whitespace
  Files: `src/qual/engine/retrieval/fts_strategy.py`, `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`
- `3b905670d081c980e3caae296aae1814909f0ad8` Add stable excerpt provenance fingerprints
  Files: `src/qual/engine/retrieval/payload.py`, `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`
- `1ac6ac38760340e02f0f9ecdc1036eb43597bd2d` Normalize FTS cache query payloads
  Files: `src/qual/engine/retrieval/fts_strategy.py`, `tests/unit/test_unified_retrieval.py`
- `8284cdef636198b9accd8a60bb0f8ff5deeb82ea` Expose canonical retrieval rank fields
  Files: `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`
- `74d6c2f81c07e14cca4137e39ae03e3467776ff1` feat(retrieval): stabilize excerpt lookup metadata
  Files: `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`
- `95610bdaa0fa955ae438eac65ab298dc6cc618af` Tighten FTS excerpt payload normalization
  Files: `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`
- `7668efb05966b8ee6eeeb2960a3862b005596a98` feat(retrieval): add excerpt lookup doc fingerprints
  Files: `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`
- `456846086d8a59cd9c86825f14c80f35e64c086c` Add retrieval query confidentiality provenance
  Files: `src/qual/engine/retrieval/payload.py`, `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`
- `7d2774e6b2d4775241283c81edac802e4a7fca2d` Fix FTS cache scope canonicalization
  Files: `src/qual/engine/retrieval/fts_strategy.py`, `tests/unit/test_unified_retrieval.py`
- `bcaec3c4cd0fc00be886c561c1690151de927dfb` Add auto excerpt retrieval alias
  Files: `src/qual/engine/retrieval/__init__.py`, `src/qual/retrieval/__init__.py`, `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`
- `4640aa4088a3121c8d7fe4843c168adfa466d61f` Harden retrieval snapshot copy safety
  Files: `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`
- `ad711fd427137a06dcf32ec7e3a692a179747f6e` Normalize sparse retrieval excerpt metadata
  Files: `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`
- `86e5b1373dcd0f64cbdecfeefad1fa4e5b290f25` Harden retrieval max-results normalization
  Files: `src/qual/engine/retrieval/__init__.py`, `src/qual/engine/retrieval/fts_strategy.py`
- `abe3c86d1abd605f4e29c7ac3a6aef29cdc28fa5` Normalize retrieval cache date ranges
  Files: `THREAD_PACKET.md`, `src/qual/engine/retrieval/fts_strategy.py`, `tests/unit/test_unified_retrieval.py`
- `3d702a22e417873e05cfb5f1a24acddb37b4d4e5` Normalize iterable retrieval strategy snapshots
  Files: `src/qual/engine/retrieval/payload.py`
- `410b8fa0dc040ae4805ecf7627fc2468ccc58ace` Normalize FTS candidate doc ids
  Files: `src/qual/engine/retrieval/fts_strategy.py`, `tests/unit/test_unified_retrieval.py`
- `1c78747a35bff9897a5ced5ddb094bbc3092cb58` Normalize retrieval document identity inputs
  Files: `src/qual/retrieval/service.py`
- `96bed1e1feb3a4708e74b768b9e3659cb0a000de` Normalize retrieval evidence strategy ids
  Files: `src/qual/engine/retrieval/payload.py`, `tests/unit/test_unified_retrieval.py`
- `77c2b937be595f8cc37c0a56add8f8e3ded1d106` Guard unresolved collection retrieval scopes
  Files: `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`
- `84f81dd0986a0e6301fb756c1b7bc7e6b88134ca` Normalize retrieval payload query snapshots
  Files: `src/qual/engine/retrieval/payload.py`
- `ded01c00cdaa76ebe13ba0cedaef0b76736b6473` Harden sparse retrieval source bundle normalization
  Files: `src/qual/engine/retrieval/payload.py`
- `78f04d16ef9425f6112957af55ed338dbee530fc` Fix retrieval excerpt lookup fingerprints
  Files: `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`
- `d528d36a257a948d6636a9609db244ed8bf8383b` Normalize sparse retrieval provenance metadata
  Files: `src/qual/retrieval/service.py`
- `44adf9cfc292cd584d5197581dbe899ff928144a` Normalize retrieval source bundle query metadata
  Files: `src/qual/engine/retrieval/payload.py`, `tests/unit/test_unified_retrieval.py`
- `c55390593445b97a28a5b4520641c2c26b70788f` fix(retrieval): canonicalize sparse excerpt query provenance
  Files: `src/qual/retrieval/service.py`
- `25c2d2095d3fd8bd618012d7184468c9aae054e2` fix(retrieval): backfill sparse payload bundles
  Files: `src/qual/engine/retrieval/payload.py`
- `58d645da3b690f4c7e653cecb3b98f7d8036de11` Strengthen retrieval evidence provenance
  Files: `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`
- `df05d063dfec3d8ed15a625a0044f090853a9011` Normalize retrieval payload date ranges
  Files: `src/qual/engine/retrieval/payload.py`, `tests/unit/test_unified_retrieval.py`
- `38d5ac17f3497f3df580db6445be5339304a9b0e` Fix FTS date-range shortlist scanning
  Files: `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`
- `fe57bbf292bbb4212c8661f261b639779d0ef7b6` Fix FTS cache date range normalization
  Files: `src/qual/engine/retrieval/fts_strategy.py`
- `2b4baa86c77494793469f5aa8e9a1025b6d3fa5b` Normalize unordered retrieval payload iterables
  Files: `src/qual/engine/retrieval/payload.py`, `tests/unit/test_unified_retrieval.py`
- `1a6a3d650bfb31e4559bce33f4f8c2789aa29b6c` Add generic retrieval excerpt fetch shim
  Files: `src/qual/engine/retrieval/__init__.py`, `src/qual/retrieval/__init__.py`
- `e8b19940cfc70e123d53c63d5846efaaa64287aa` Normalize retrieval lookup metadata
  Files: `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`
- `b3894bb1de384742d2d5aa7ab72af99e9ca770b8` Tighten retrieval bundle citation backfills
  Files: `src/qual/engine/retrieval/payload.py`, `tests/unit/test_unified_retrieval.py`
- `d5bf24f372d1709b450d33c7d99387922d9a7957` feat(retrieval): add basket promotion snapshot
  Files: `src/qual/engine/retrieval/payload.py`, `src/qual/retrieval/service.py`
- `cc3c1fd8a4ec43da6131e9b78708a410ee6327fc` feat(retrieval): harden basket promotion backfill
  Files: `src/qual/engine/retrieval/payload.py`, `tests/unit/test_unified_retrieval.py`
- `f1188111f599924d7738029e1cf70b1b4a877351` fix(retrieval): backfill basket promotion from source bundles
  Files: `src/qual/engine/retrieval/payload.py`, `tests/unit/test_unified_retrieval.py`
- `86cc1c6efdb524113d05471e4ca0c8e4134bfa7f` fix(retrieval): reject non-fts excerpt normalization
  Files: `src/qual/retrieval/service.py`
- `4a4c4fc2d7749405647490f0b0301b6330feee99` Export fetch_excerpt from engine retrieval facade
  Files: `src/qual/engine/retrieval/__init__.py`, `tests/unit/test_unified_retrieval.py`
- `6b7822de029c44bc1020688610430f21411e6d6d` Clarify retrieval packet ownership note
  Files: `THREAD_PACKET.md`, `codex_packet_handoff/tools/planner.py`, `tests/unit/test_packet_planner.py`
- `0b07b3c6e4c0b918c80f029d40ada84aeebc9873` fix(retrieval): normalize sparse excerpt lookup metadata
  Files: `src/qual/retrieval/service.py`
- `f98bca04dadd4c819583d97028c6db128f809196` feat(retrieval): preserve excerpt provenance for basket promotion
  Files: `src/qual/engine/retrieval/payload.py`, `src/qual/retrieval/service.py`
- `629f7c27f8aea0f0299f516126f41cd40065d70b` Fix retrieval provenance backfill from citations
  Files: `src/qual/engine/retrieval/payload.py`, `tests/unit/test_unified_retrieval.py`
- `bc5e2f1d5cf17758e21b229921e9281219b9bc09` fix(retrieval): normalize provenance span snapshots
  Files: `THREAD_PACKET.md`, `src/qual/engine/retrieval/payload.py`, `src/qual/retrieval/service.py`
- `0a9c37c38fd91c981c93e31ee3d38caf31f9e52d` Harden doc-only retrieval basket provenance
  Files: `src/qual/engine/retrieval/payload.py`, `tests/unit/test_unified_retrieval.py`
- `168ee849304999df4127eeba1c36d8f6f889a6c3` chore(retrieval): drop packet-planner drift
  Files: `codex_packet_handoff/tools/planner.py`, `tests/unit/test_packet_planner.py`
- `9acb7e58a07dabc4bccda81cff5ce774c9851d3f` Align retrieval doc citation provenance
  Files: `src/qual/engine/retrieval/payload.py`, `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`
- `6ca8da126b3ce3241cba2d04ba6ddb57cab09e2e` Harden retrieval citation normalization
  Files: `src/qual/engine/retrieval/payload.py`, `tests/unit/test_unified_retrieval.py`
- `31268ec26c5bfa26cd572b6528ea4f65a588911f` fix(retrieval): normalize nested citation bundles
  Files: `src/qual/engine/retrieval/payload.py`
- `c60234b1a281802aef92415d6f62145ad4929259` fix(retrieval): validate canonical excerpt ids
  Files: `src/qual/retrieval/service.py`
- `30c029c9611f6f78c790a3b9d273e3cceaa7b1cc` fix(retrieval): stabilize unordered constraint inputs
  Files: `src/qual/engine/retrieval/__init__.py`
- `2631c81affba326cf57072f675cba64ed4506cb9` Align FTS cache query normalization
  Files: `src/qual/engine/retrieval/fts_strategy.py`
- `777db926649f2af40f1dfd5c8efa090d8518d25e` Add doc type to retrieval basket promotion
  Files: `src/qual/engine/retrieval/payload.py`, `src/qual/retrieval/service.py`
- `71f4ae12a7ca50c029af92da9a7856640d1c8a49` feat(retrieval): expose basket promotion in context bundle
  Files: `src/qual/engine/retrieval/payload.py`, `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`
- `6162bcbe1b8dc308014abd312d9fabbf495c1224` Enforce FTS-only engine excerpt lookup
  Files: `src/qual/engine/tools/excerpt_tools.py`, `tests/unit/test_unified_retrieval.py`
- `0af43546ce817bc4e0173a24210beb0601bd0e0c` feat(retrieval): add excerpt basket promotion payload
  Files: `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`
- `ddc12cff8063a6f6aa031b05b944475de15e9ff7` feat(retrieval): preserve basket promotion evidence
  Files: `src/qual/engine/retrieval/payload.py`, `src/qual/retrieval/service.py`
- `eb75358d059707a8a12c27ec081cd6014143aaf3` fix(retrieval): preserve basket promotion in context backfill
  Files: `src/qual/engine/retrieval/payload.py`, `tests/unit/test_unified_retrieval.py`
- `1700cbe6a85550f97731fc5040e38d25ae6b0b9e` feat(retrieval): fingerprint excerpt lookup promotion
  Files: `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`
- `213cfcda16d979cff68af5da46b4db85b12c84f5` Tighten missing doc-scope retrieval provenance
  Files: `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`
- `65b6bf75da7605966f65a80b775dabfb080b9220` feat(retrieval): carry policy through basket promotion
  Files: `src/qual/engine/retrieval/payload.py`, `src/qual/retrieval/service.py`
- `d264cf25c9101798ea784b3b38bf516a89c5890a` Normalize retrieval evidence date ranges
  Files: `src/qual/engine/retrieval/payload.py`, `tests/unit/test_unified_retrieval.py`
- `d59ca648bf2a327a6fdd276247a455cad0ab4f20` fix(retrieval): regenerate handoff for true branch scope
  Files: `THREAD_PACKET.md`, `src/qual/engine/tools/excerpt_tools.py`, `tests/unit/test_unified_retrieval.py`
- `11caf9e2de219846ef13551793dfae05253b2ed2` feat-retrieval-fts: enrich retrieval context bundles
  Files: `src/qual/engine/retrieval/payload.py`, `src/qual/retrieval/service.py`
- `50d618f0e796e6a7b5e9f8f1df94cecd828630e6` Tighten retrieval basket promotion context
  Files: `src/qual/engine/retrieval/payload.py`, `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`
- `8339c6552ed833b7878ac600e946df54ef29bc0c` feat(retrieval): carry source bundle fingerprints through context
  Files: `src/qual/engine/retrieval/payload.py`, `src/qual/retrieval/service.py`
- `1036ff99bc501cba4976ffd54c530b83f440e7f7` Tighten retrieval summary provenance
  Files: `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`
- `9937c159ab1a456686e5586e2ad323ff1b75ebad` Normalize retrieval payload query context
  Files: `THREAD_PACKET.md`, `src/qual/engine/retrieval/payload.py`
- `84193730ef74cf5afa41a5cf258ce2839f546af5` Fail fast for deferred retrieval scopes
  Files: `src/qual/retrieval/service.py`
- `1e0cce267a9b06e48ab485c901884b2b5fed7ff3` Tighten retrieval provenance promotion snapshot
  Files: `src/qual/engine/retrieval/payload.py`, `src/qual/retrieval/service.py`
- `6d532146b627c148129f0f4aad391b784ae0a725` Fix retrieval basket promotion backfill
  Files: `src/qual/engine/retrieval/payload.py`, `tests/unit/test_unified_retrieval.py`
- `e744fe89c74abe487ebcd5df76282149f89de6bb` Harden retrieval lookup promotion metadata
  Files: `src/qual/engine/retrieval/payload.py`, `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`
- `4dfc09848f7c7a68d45ce139758e2bf32479532b` fix(retrieval): canonicalize excerpt lookup payload ids
  Files: `src/qual/retrieval/service.py`
- `2f6b4454e3d4a8fa2a5cb42452c213d71b11e2dc` Normalize basket promotion retrieval fields
  Files: `src/qual/engine/retrieval/payload.py`, `tests/unit/test_unified_retrieval.py`
- `655e4a2179adcda954b59922999c379c112b507f` fix(retrieval): normalize excerpt lookup payload text
  Files: `src/qual/retrieval/service.py`
- `9ae8e5e888302964cbda4e1ab6c4d7efb4a2eebf` Normalize retrieval citation snapshots
  Files: `src/qual/engine/retrieval/payload.py`, `tests/unit/test_unified_retrieval.py`
- `49b540f7dd16825859819ddf30b09f3cc8ff191f` fix(retrieval): include promotion strategies in payload
  Files: `src/qual/retrieval/service.py`
- `0bf7ccda2294e87cbca054b7eea3b89d0db62ab8` Fix source-bundle context payload reconstruction
  Files: `src/qual/engine/retrieval/payload.py`, `tests/unit/test_unified_retrieval.py`
- `5f1f7c6275dd0e3f4d4c910e43d0426390476aa0` Normalize retrieval basket promotion identities
  Files: `src/qual/engine/retrieval/payload.py`, `tests/unit/test_unified_retrieval.py`
- `dfb5909621021c31574f6d9b971c38d44eac4621` Tighten FTS excerpt lookup normalization
  Files: `src/qual/retrieval/service.py`
- `6a1ab856f70c70fd69c661a5f66b7e95f96470dd` Normalize retrieval provenance snapshots
  Files: `src/qual/engine/retrieval/payload.py`
- `cc50e34eb18907b6167f38ca4b7864c6bb08ca2f` Preserve FTS shortlist order in excerpt lookups
  Files: `src/qual/retrieval/service.py`
- `c162148380388589a552b1d722889d0fca9f5bdf` Add ranked ids to retrieval basket promotion
  Files: `src/qual/engine/retrieval/payload.py`, `src/qual/retrieval/service.py`
- `c073ad1ffeba08fdc6930b34495d5f8abadf9f16` Normalize retrieval helper max-results
  Files: `src/qual/engine/retrieval/payload.py`, `tests/unit/test_unified_retrieval.py`
- `e7958b4656b045844262c3547cae0011446faef1` Align excerpt lookup policy payloads
  Files: `src/qual/retrieval/service.py`
- `6128311b57ca36d746b535772f513f6d37c7c683` feat-retrieval-fts: enrich excerpt lookup audit
  Files: `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`
- `33619883867fb1f3bb5f5ff935deb3f555858712` feat-retrieval-fts: stabilize empty retrieval source bundles
  Files: `src/qual/engine/retrieval/payload.py`
- `16403079b72893e52c0d756060ddf50c1386af39` fix retrieval provenance backfill from basket snapshot
  Files: `src/qual/engine/retrieval/payload.py`
- `2828006c429bb7b6980ff854a48ef1dee1b61645` feat-retrieval-fts: preserve doc-scoped shortlist provenance
  Files: `src/qual/retrieval/service.py`
- `dfbbf39b943fe35f3e76528e56fe575aa8f8bf20` feat(retrieval): preserve lookup ranked ids
  Files: `THREAD_PACKET.md`, `src/qual/retrieval/service.py`
- `661f4cfe7f9083917cc985a99a676280c43bbf63` Tighten retrieval excerpt lookup fingerprints
  Files: `src/qual/retrieval/service.py`
- `1ba93a97f4a8379d19606d9fc2c7a7232eaf1ade` feat(retrieval): surface hit strategy context
  Files: `src/qual/retrieval/service.py`
- `94b393254e049c0909824d0a2267f00622903011` retrieval: backfill lookup title hints from provenance
  Files: `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`
- `724b86e03e20b233bd603779e5ce0695bcf11502` retrieval: rehydrate sparse context bundle fields
  Files: `src/qual/engine/retrieval/payload.py`
- `7a053402f83c6d3365e944612b577e2b56bd870b` Harden retrieval provenance list normalization
  Files: `src/qual/retrieval/service.py`
- `fa4b7a0ea2cef480450473471801368693cee976` retrieval: normalize canonical query inputs
  Files: `src/qual/engine/retrieval/__init__.py`, `tests/unit/test_unified_retrieval.py`
- `32b4452466fb2344796c9e748c945efc040cf83b` Normalize context-only retrieval helpers
  Files: `src/qual/engine/retrieval/payload.py`
- `a11f9cbc4b1dbebefcfbeea2826aed69e4cb856f` Fix basket promotion boolean normalization
  Files: `src/qual/engine/retrieval/payload.py`, `tests/unit/test_unified_retrieval.py`
- `45b3489589fcace80c544405b8ad12899b207c15` Preserve auto excerpt audit entrypoint
  Files: `src/qual/retrieval/service.py`
- `fc56ffd351cb18897a29c43bf7f539bb8c576dc8` Harden retrieval span normalization
  Files: `src/qual/engine/retrieval/payload.py`, `src/qual/retrieval/service.py`
- `8584e92a69be18a60caa6fc58a7e394c82849fd0` Add excerpt lookup retrieval IDs to audit
  Files: `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`
- `aa298ca746384bd4222fb03cd8813590742b7908` Normalize basket promotion excerpt text
  Files: `src/qual/engine/retrieval/payload.py`, `tests/unit/test_unified_retrieval.py`
- `0d46dd929269b2f1618fe8315e80d8454db555de` Add source bundle fingerprint to basket promotion
  Files: `src/qual/engine/retrieval/payload.py`, `src/qual/retrieval/service.py`
- `6c753a3dfd56fafdec0796b638d5a4272a48877c` Harden retrieval source bundle snapshots
  Files: `src/qual/retrieval/service.py`
- `2927b494e6dbef6dbdef708b9cb9953ca9be8110` Carry retrieved ids in retrieval provenance
  Files: `src/qual/engine/retrieval/payload.py`, `src/qual/retrieval/service.py`
- `993140c6218a977335cdf35aa49f8d9b37278a72` Add basket promotion fingerprints
  Files: `src/qual/engine/retrieval/payload.py`, `src/qual/retrieval/service.py`
- `fbf758416021d46a01fd40bf33dd55789f7102e9` Normalize retrieval date-range fingerprints
  Files: `src/qual/engine/retrieval/fts_strategy.py`, `src/qual/engine/retrieval/payload.py`, `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`
- `b3554ecae4c443d6a5a03d8a797fb350f5479043` Add canonical query snapshot to excerpt payloads
  Files: `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`
- `b8db9eea18e411af2e1a06f5ebf7c8c76d47c026` Normalize sparse retrieval query snapshots
  Files: `src/qual/engine/retrieval/payload.py`
- `d21c14df7d8b7ca375309b6c6e883a392b700a9b` feat(retrieval): preserve lookup query constraints
  Files: `src/qual/retrieval/service.py`
- `89e2a12cd84e75820c694020f41558282d9593f5` feat(retrieval): backfill excerpt query constraints
  Files: `src/qual/retrieval/service.py`
- `342612c1fbfb4ae776b22ad5ec7e6af187d6fcf9` fix(retrieval): mark doc-backed promotions auditable
  Files: `src/qual/engine/retrieval/payload.py`, `src/qual/retrieval/service.py`
- `0118722a6a9d591eae03073c1a438c4e9caf6d4c` fix(retrieval): preserve top excerpt anchors in basket promotion
  Files: `src/qual/engine/retrieval/payload.py`
- `c9cb88213f38b6e7b577a750f0098c1e9bd5f8fe` fix(retrieval): preserve doc-backed excerpt provenance fingerprint
  Files: `src/qual/engine/retrieval/payload.py`, `src/qual/retrieval/service.py`
- `a23e45b02a8f21092f99852325e88c983f1ba862` fix(retrieval): deep copy normalized payload items
  Files: `src/qual/engine/retrieval/payload.py`
- `c0d9ef3520f490da556d6fa88b979dadc548ea4e` Tighten retrieval basket promotion backfill
  Files: `src/qual/engine/retrieval/payload.py`
- `d9b31d115f7c4266f5454f3ce269d92fca5f5271` fix(retrieval): backfill basket anchors from provenance
  Files: `src/qual/engine/retrieval/payload.py`, `tests/unit/test_unified_retrieval.py`
- `82fe746eb8d59ecb591e4fec5ad0c0373f8cd9b7` fix(retrieval): isolate fresh FTS hits from cache state
  Files: `src/qual/engine/retrieval/fts_strategy.py`
- `fdaf97d57569d94f14698c9eed6cb1428a69be89` Harden lookup span normalization
  Files: `src/qual/retrieval/service.py`
- `dbeb14956e63d8e0eace0d40d7a7acf8cb626562` retrieval: backfill sparse excerpt title hints
  Files: `src/qual/retrieval/service.py`
- `d5018d665818d7b1579e96b92060ef8a562e6eb3` Harden sparse retrieval query confidentiality
  Files: `src/qual/engine/retrieval/payload.py`
- `d9446cfeb556cadd1aaee98cc127f52b31f2a0fa` fix retrieval basket promotion fingerprint normalization
  Files: `src/qual/engine/retrieval/payload.py`, `tests/unit/test_unified_retrieval.py`
- `645b1d06029c52861c208682a29d73c90f850141` Fix confidential sparse retrieval title hints
  Files: `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`
- `0f71f0a5360e9fea2d0e828353ac477bf43b270b` Normalize excerpt query snapshot defaults
  Files: `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`
- `3427962ade792c7dd5bff0ac41a58b14cbf3c136` Tighten retrieval shim delegation
  Files: `src/qual/engine/retrieval/__init__.py`, `src/qual/retrieval/__init__.py`, `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`
- `8b219039ab16d934eb41b96d5143504e203f644e` Audit failed FTS excerpt lookups
  Files: `src/qual/retrieval/service.py`
- `0ec7cd0c8aa171a01b0367ebac830f4efe4ff367` Snapshot retrieval result payload state
  Files: `src/qual/retrieval/service.py`
- `ab84e9ed577cae2a699fddf8d5e9ad2e6cfebbea` Backfill nested excerpt query metadata
  Files: `src/qual/retrieval/service.py`
- `148df4d7522ff95bdadc498a30689b36f6fe20de` Stabilize retrieval lookup promotion metadata
  Files: `src/qual/retrieval/service.py`
- `0201b55ec935b7084d8801cd4ad45b4aa00462ec` Normalize retrieval section hints
  Files: `src/qual/retrieval/service.py`
- `054db914848c6310c857c17a5d8fc1589502acf8` Backfill excerpt query fingerprints
  Files: `src/qual/retrieval/service.py`
- `2e4422a0d9a41745b7b98056967d8221e2eedab2` Preserve retrieval title hints in sparse bundles
  Files: `src/qual/engine/retrieval/payload.py`, `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`
- `bb9e0598c1d93e1f4db41e46135c2f52892ca476` Align excerpt lookup audit with canonical payload
  Files: `src/qual/retrieval/service.py`
- `793ac7336d84fabaf50f83196da7620cb0352938` Harden excerpt lookup audit provenance
  Files: `src/qual/retrieval/service.py`
- `2944937fb8b54a6f118b349797ddf4df201d6cb1` Tighten FTS cache scope normalization
  Files: `src/qual/engine/retrieval/fts_strategy.py`
- `cd1a70411a6ef9940858a2aec2691f459f0bae56` retrieval: include basket promotion in bundle snapshots
  Files: `src/qual/engine/retrieval/payload.py`, `src/qual/retrieval/service.py`
- `be0d9c7f8f1ba0babf812aec2a793e24e979d5ce` Normalize retrieval hit provenance snapshots
  Files: `src/qual/retrieval/service.py`
- `599eb574cbeeebb3a8f0472056682f548191d283` Normalize retrieval payload hit snapshots
  Files: `src/qual/engine/retrieval/payload.py`
- `6d4fba4be56dca5c4b0f0a5a91436d65ac2fa679` retrieval: backfill mirrored hit provenance
  Files: `src/qual/engine/retrieval/payload.py`
- `f74d72224222a43e84f77e9c4d8b80135ba51cce` retrieval: mirror doc hit top-level fields
  Files: `src/qual/engine/retrieval/payload.py`, `src/qual/retrieval/service.py`
- `9e30219e9507f77da1fef27ab827f58ad55a7e56` retrieval: preserve canonical hit order
  Files: `src/qual/retrieval/service.py`
- `dc7ee2510e7ff711284f2901ad7e6f20aceadb18` retrieval: persist excerpt query provenance
  Files: `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`
- `7aaf5da5dbed9c6189574513d1fa91ddc3a84b88` Invalidate stale excerpt retrieval context
  Files: `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`
- `51f92ca2d461f328de6a663168bc3a6966e7a9a3` Tighten stale excerpt query payloads
  Files: `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`
- `8c42658a2587008684a1a9c0d896779107825613` Normalize excerpt lookup section hints
  Files: `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`
- `701359361807cdd70b91254c356ad585055d3357` retrieval: persist explicit retrieved ids in summaries
  Files: `src/qual/engine/retrieval/payload.py`, `src/qual/retrieval/service.py`
- `a348c5f73f9c34b26e3758637491c0a0c772c4f9` retrieval: preserve policy alias in provenance
  Files: `src/qual/retrieval/service.py`
- `28457ed9f4c3117755527ddfd4837b0f779717b9` Preserve canonical query in retrieval bundles
  Files: `src/qual/engine/retrieval/payload.py`, `src/qual/retrieval/service.py`
- `cf866ba3839dfb9f072447afac71f088b036dee0` Harden excerpt query context defaults
  Files: `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`
- `95eee546b699be4ecc85560d0b440b8c5c23c82e` retrieval: carry query text in basket promotion
  Files: `src/qual/engine/retrieval/payload.py`, `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`
- `5adbeb7b939ce3159d8e51e0b4e59fa0ae83dc6e` Prune stale retrieval excerpt contexts
  Files: `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`
- `1d0b5377bff5a5b45845c0f00e7f106eeae6f2ed` retrieval: preserve policy alias in context bundles
  Files: `src/qual/engine/retrieval/payload.py`, `src/qual/retrieval/service.py`
- `64b356d4334f8a25d46370e7244dc968b28aa6e2` feat(retrieval): fail closed on deferred fts scopes
  Files: `src/qual/engine/retrieval/fts_strategy.py`
- `4ef97ca975ff3ddcc32ffd9cf855e4c8a2506271` fix(retrieval): stabilize downstream diagnostics
  Files: `src/qual/retrieval/service.py`
- `b045aca4a935b864a333badc7003a90d08f6bf88` Harden retrieval payload ID normalization
  Files: `src/qual/engine/retrieval/payload.py`
- `b0a239a1df96ccc149185b6936dba83b28f7b678` Normalize FTS cache query variants
  Files: `src/qual/engine/retrieval/fts_strategy.py`, `tests/unit/test_unified_retrieval.py`
- `838b4c4251e19e2f685267215198cff8a38d3f1f` Backfill sparse retrieval hit provenance
  Files: `src/qual/engine/retrieval/payload.py`, `tests/unit/test_unified_retrieval.py`
- `552ba2fb9dc853e30b76044f18ba3b0ccee367c1` Normalize retrieval citation bundle metadata
  Files: `src/qual/engine/retrieval/payload.py`
- `17d1cdb459665dfd1ed687307f0c24b59d262b52` feat(retrieval): align canonical citation bundle surface
  Files: `src/qual/engine/retrieval/payload.py`, `src/qual/retrieval/service.py`
- `245ddb91b906caf392797830468606ec1101c3d2` fix(retrieval): fail closed on sparse excerpt query context
  Files: `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`
- `d900d077cefc182e5ef95141dbb68106167e44f9` feat(retrieval): carry query constraints into basket promotion
  Files: `src/qual/engine/retrieval/payload.py`, `src/qual/retrieval/service.py`
- `cc6190fde2f6505f18847f293ef29ebb9f766fa1` fix(retrieval): normalize rebuilt section hints
  Files: `src/qual/engine/retrieval/payload.py`
- `8c19b3ccc5138ce2bb0ed880dab2091b307fef5b` Add retrieval policy alias to source bundles
  Files: `src/qual/engine/retrieval/payload.py`, `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`
- `46f33b00a754f313f6149ca45d47681d43440b13` fix(retrieval): alias policy in promotion snapshots
  Files: `src/qual/engine/retrieval/payload.py`, `src/qual/retrieval/service.py`
- `aa50181a26a8bbc073ada64ccd21ae275a386343` fix(retrieval): normalize shortlist ids in snapshots
  Files: `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`
- `5d9af74773ea96b0fbc65697effec4819e282075` Tighten retrieval query fingerprint normalization
  Files: `src/qual/retrieval/service.py`
- `2a770cc76f9fb4ce26e7d15e358413d6b6baffae` Normalize basket promotion doc types
  Files: `src/qual/engine/retrieval/payload.py`, `tests/unit/test_unified_retrieval.py`
- `dffc085dd9a2cb98393e113f1c3a9952f57dd4b4` feat: expose excerpt lookup query constraints
  Files: `src/qual/retrieval/service.py`
- `e398c81caafee19dd55b6b62f9bc57615b0b05c8` fix(retrieval): carry query constraints into lookup audit
  Files: `src/qual/retrieval/service.py`
- `6b783b60b840c5fd63c3b07b19aa0c67ebf09081` Add primary retrieval citations to provenance
  Files: `src/qual/engine/retrieval/payload.py`, `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`
- `7bd332628dddf1912710436094c2144cffa7ef21` Normalize retrieval hit spans
  Files: `src/qual/retrieval/service.py`
- `69456f6b8ce84287f45280e6fbb40e409be9e002` fix(retrieval): clear orphaned sparse query mirrors
  Files: `src/qual/retrieval/service.py`
- `0bf3263dbcc96d1b94cb890c27bfd4a2375ba61d` fix(retrieval): fail closed on orphaned excerpt query fingerprints
  Files: `src/qual/retrieval/service.py`
- `50c318b17cc2b90d73602d6ec5bdd805dbd2f003` fix(retrieval): harden excerpt promotion query metadata
  Files: `src/qual/retrieval/service.py`
- `d9542206f6fd14db37d1ddf5efd76f941d32314b` Fix retrieval packet demo-path mapping
  Files: `codex_packet_handoff/tools/planner.py`, `tests/unit/test_packet_planner.py`
- `4a640a05f7bf391aca8973b028bdb97c0556b6ea` fix(retrieval): fingerprint provenance snapshots
  Files: `src/qual/engine/retrieval/payload.py`, `src/qual/retrieval/service.py`
- `4d4546a0c936947a3109d2a218ffe135997afb12` Fix sparse retrieval query rehydration
  Files: `src/qual/retrieval/service.py`
- `ced0bcaf3d5446d549b04d1bc24593eda8850266` fix(retrieval): prefer canonical excerpt query snapshots
  Files: `src/qual/retrieval/service.py`
- `b8ae6c7a0e73d9d3ec5e1024ceb1c34d232e46c6` Avoid rewriting FTS index on read queries
  Files: `src/qual/retrieval/service.py`
- `59752724035b5d241e51b3d3f89248947f22c7e1` Avoid redundant excerpt context rewrites
  Files: `src/qual/retrieval/service.py`
- `edd5380ab2aafe6dc83c6d4d6b2222b1256f20a2` fix retrieval basket query backfill
  Files: `src/qual/engine/retrieval/payload.py`, `tests/unit/test_unified_retrieval.py`
- `df572a69b70be8342450552bea0aa2e4bf125deb` Harden retrieval boolean constraint normalization
  Files: `src/qual/engine/retrieval/__init__.py`, `src/qual/engine/retrieval/fts_strategy.py`
- `850eacce56c3c3e59a2ec0509ffbe58b69f3e636` fix retrieval payload helper precedence
  Files: `src/qual/engine/retrieval/payload.py`, `tests/unit/test_unified_retrieval.py`
- `29e31e9d0e2dfa9ca6fbf041960ba1b8030bd48c` Fix sparse retrieval query constraint rehydration
  Files: `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`
- `11d7079e3652cbcf14e9de2524b37ef2f8ab8a05` Fix sparse query_constraints rehydration
  Files: `src/qual/retrieval/service.py`
- `4c409ea4666a5e0cef7aa7bd18aa79b31ab3cf86` test(packet): align retrieval handoff wording
  Files: `tests/unit/test_packet_planner.py`
- `f1bc4906cb46c49ad2f1fd07eabc1d7d3e0db817` Harden sparse excerpt query constraint backfill
  Files: `src/qual/retrieval/service.py`
- `381e328a9cccc73cfb75ae299d2f4c2574d3403a` Fail closed sparse retrieval lookup confidentiality
  Files: `src/qual/retrieval/service.py`
- `845fcfb99a6254d2a21e7c9c54708726a897d193` fix retrieval strategies-used audit semantics
  Files: `src/qual/engine/retrieval/payload.py`, `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`
- `66b288ef3cfb875e24b4fb2771f202b7cb9bf543` Normalize retrieval hit shortlist snapshots
  Files: `src/qual/engine/retrieval/payload.py`, `tests/unit/test_unified_retrieval.py`
- `153c69392ce0c7ab36c876f6b9f153f0493503ed` Redact query text from excerpt lookup audit
  Files: `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`
- `c8df93427a6974883518f7857b015fb7424795ce` Backfill nested retrieval query metadata
  Files: `src/qual/engine/retrieval/payload.py`, `tests/unit/test_unified_retrieval.py`
- `a9eaaaa7d60a39464b801bd7e6cbcec467e77a3d` feat(retrieval): mirror basket promotion source strategy
  Files: `src/qual/engine/retrieval/payload.py`, `src/qual/retrieval/service.py`
- `18498590167ae9c1f0a2393cef1de338da8b63df` fix(retrieval): enrich failed excerpt lookup audit
  Files: `src/qual/retrieval/service.py`
- `e8a8717b138f7d3551cd89bc3dc68071d5dad5f3` fix(retrieval): align failed excerpt lookup audit shape
  Files: `src/qual/retrieval/service.py`
- `791668c7543f00f964fb2290b3831c3d6d7dd611` fix(retrieval): align excerpt lookup audit aliases
  Files: `src/qual/retrieval/service.py`
- `cf644d98c43cc396cd5b7c6b8d725b87fb715c61` fix: fail close canonical retrieval payload rebuilds
  Files: `src/qual/engine/retrieval/payload.py`, `tests/unit/test_unified_retrieval.py`
- `5148e26650fe64ef05c5820556552cfc7840ff7a` fix(packet): tighten retrieval demo-path wording
  Files: `THREAD_PACKET.md`, `codex_packet_handoff/tools/planner.py`, `docs/gate_passed.txt`, `tests/unit/test_packet_planner.py`
- `9835d7a5b641f5e08ad2dea85c5af033efba6435` Harden FTS strategy hit snapshots
  Files: `THREAD_PACKET.md`, `src/qual/engine/retrieval/fts_strategy.py`
- `206ee919c0bb7a1736e07a86a5cba5aff314a785` fix(retrieval): normalize empty FTS runner hits
  Files: `src/qual/engine/retrieval/fts_strategy.py`, `tests/unit/test_unified_retrieval.py`
- `a96043fee95c3be1b69fba0148e6fdbb5d1d51a9` feat(retrieval): mirror query constraints on hit snapshots
  Files: `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`
- `9d9e11a1929dc56e44f5a4d459aa385e7a6ce1e5` fix(retrieval): preserve mirrored query constraints on sparse hits
  Files: `src/qual/engine/retrieval/payload.py`
- `2a136e56b78470a1a579f3cca73397a58b08622a` Fix sparse retrieval citation ordering
  Files: `src/qual/engine/retrieval/payload.py`, `tests/unit/test_unified_retrieval.py`
- `18f0ab0960c6d07920de212785c9517e8688418c` fix(retrieval): align sparse primary citations
  Files: `src/qual/engine/retrieval/payload.py`
- `7fb9b3cb389e424fcbc0d54cb2087421fe8c6727` fix(retrieval): expose canonical provenance bundle alias
  Files: `src/qual/engine/retrieval/payload.py`, `src/qual/retrieval/service.py`
- `416d3293d064b6e7fb05a7e8997d91bddbef443f` Harden sparse FTS excerpt query rehydration
  Files: `src/qual/retrieval/service.py`
- `8f5981a4fdfab52fe4346340c927abf9b9e38b45` Guard FTS strategy scope execution
  Files: `src/qual/engine/retrieval/fts_strategy.py`
- `6a3adae55cdcf6a5717ef2ae79b5d0c03559bdb8` Tighten retrieval handoff plan mapping
  Files: `THREAD_PACKET.md`, `codex_packet_handoff/tools/planner.py`, `docs/gate_passed.txt`, `tests/unit/test_packet_planner.py`
- `4387c7277d8d983012d970312a6bcc14f6fb571d` fix(retrieval): canonicalize hit provenance strategy metadata
  Files: `src/qual/retrieval/service.py`
- `6ed15b42efa484dc7d0db8e3f2c37fdb8a34eb35` fix(retrieval): audit failed excerpt lookups as fts attempts
  Files: `THREAD_PACKET.md`, `docs/gate_passed.txt`, `src/qual/retrieval/service.py`
- `d3e011f20985353fe6e18ee7b25411ff2f1556be` fix(retrieval): align failed excerpt lookup audit schema
  Files: `THREAD_PACKET.md`, `docs/gate_passed.txt`, `src/qual/retrieval/service.py`
- `7372c97fcee7f8a0ab1aea22b25d58bbff0e7eb9` fix(retrieval): align excerpt lookup success audit schema
  Files: `src/qual/retrieval/service.py`
- `e98544753c7e5797abeeeb5e59bbe7d3517d42a4` perf(retrieval): cache engine retrieval facade import
  Files: `src/qual/engine/retrieval/__init__.py`
- `71bd4563b7df067695423e11e17054be570cc9d1` Tighten FTS strategy scope gating
  Files: `src/qual/engine/retrieval/fts_strategy.py`
- `bf1f0da3ead9c4ba60e8f083c0a724acd4dd2473` Fix retrieval excerpt API scope
  Files: `THREAD_PACKET.md`, `docs/gate_passed.txt`, `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`
- `92d9f4bd996ba88660bbc410c5e97005ff0713b6` fix(retrieval): preserve generic excerpt compatibility
  Files: `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`
- `9da45e5acb286aac881d472fca2086d071ed6b57` fix(retrieval): restore fetch_excerpt compatibility fallback
  Files: `src/qual/retrieval/service.py`
- `cfda7c59c2dc46d2ca2e3038a94d342c73ea4b5a` fix(retrieval): restore fts-only excerpt contract
  Files: `THREAD_PACKET.md`, `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`
- `94dc75613d14b3a610bbf39c15cbe71cdd705f99` test(retrieval): cover fail-closed excerpt facade
  Files: `THREAD_PACKET.md`, `tests/unit/test_unified_retrieval.py`
- `2b03f9a218ce3444bb2e49d8204ceebbcfe82ad7` fix(retrieval): preserve canonical query in provenance bundle
  Files: `src/qual/engine/retrieval/payload.py`, `src/qual/retrieval/service.py`
- `3d362dd419079f6fbc42e0ae0a00e882fbd8cb15` fix(retrieval): fail closed for noncanonical fts queries
  Files: `THREAD_PACKET.md`, `src/qual/engine/retrieval/fts_strategy.py`
- `36a8b1e5e99a17c6eec1235557cfff8463061037` Tighten retrieval handoff demo-path scope
  Files: `THREAD_PACKET.md`, `codex_packet_handoff/tools/planner.py`, `tests/unit/test_packet_planner.py`
- `367215ec570ab39490567bf14758ee25b61de457` retrieval: localize canonical query builder
  Files: `src/qual/retrieval/__init__.py`
- `9e02450b28a598afddeecb0466af7fcb724f942b` fix(retrieval): delegate engine query builder
  Files: `src/qual/engine/retrieval/__init__.py`
- `f310336ed561c8c126ff279d1368df88d7bc6e6c` Mirror query section hints in retrieval payloads
  Files: `src/qual/engine/retrieval/payload.py`, `src/qual/retrieval/service.py`
- `b3a31ec52225191b0362918231fc9973ab45317a` fix(retrieval): reorder reconstructed hit snapshots
  Files: `src/qual/engine/retrieval/payload.py`
- `fe5e83d7886f9f7403b0322df574877eb63c9e8e` fix(retrieval): drop packet planner drift
  Files: `codex_packet_handoff/tools/planner.py`, `tests/unit/test_packet_planner.py`
- `d08431dd831dc6d971502fd3825faf55dced7c3a` fix(retrieval): clear planner drift remainder
  Files: `codex_packet_handoff/tools/planner.py`
- `4ec62ffecef5ee266d766cbb35ffc531cd597e60` fix(retrieval): fail closed on unsupported scoped queries
  Files: `src/qual/engine/retrieval/fts_strategy.py`, `tests/unit/test_unified_retrieval.py`
- `508c85184ac7bb55e7dbdf44cc0282ed748e1262` feat(retrieval): label excerpt lookup context status
  Files: `src/qual/retrieval/service.py`
- `3dbe1a4ccffb820b197229162da0fd403bdcfbed` fix(retrieval): preserve lookup query context status
  Files: `src/qual/engine/retrieval/payload.py`
- `1d9423f4399e753734f5b23dee667be76f74eda4` fix(retrieval): backfill lookup provenance context
  Files: `src/qual/engine/retrieval/payload.py`, `tests/unit/test_unified_retrieval.py`
- `7917500c1f79b0aef337e8b46fb118a35d58016c` fix(retrieval): rebuild canonical payloads from lookup snapshots
  Files: `src/qual/engine/retrieval/payload.py`
- `1eaf77adace04274f20e1ff596fad89f4e06b8bf` fix(retrieval): mirror query text on hit payloads
  Files: `src/qual/engine/retrieval/payload.py`, `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`
- `9bd108298e82f2ba9cc1a6ab97d2f20f7dc622fe` fix(retrieval): resolve engine query annotations
  Files: `src/qual/engine/retrieval/__init__.py`
- `255bf8d81801cfd21aa8dc5c9db5d5e11c3efa2b` fix(retrieval): backfill sparse hit query context
  Files: `src/qual/engine/retrieval/payload.py`
- `6a41f0f118163f4fa8082cda04789c54ed796e34` fix(retrieval): mirror provenance query constraints
  Files: `src/qual/engine/retrieval/payload.py`, `src/qual/retrieval/service.py`, `tests/unit/test_unified_retrieval.py`
- `ed0995f552723203222f938fe2b4c07b76c1929d` Guard FTS candidate doc id inputs
  Files: `src/qual/engine/retrieval/fts_strategy.py`, `tests/unit/test_unified_retrieval.py`
- `0a222d08310c907b67e6ce9d1585d55cd00d88aa` fix(retrieval): preserve mirrored excerpt query context
  Files: `src/qual/retrieval/service.py`
- `b9e32dbc1b65b4b4c8d5c3bffb4223f9b681eeb0` fix(retrieval): lazy-bind engine retrieval runtime types
  Files: `src/qual/engine/retrieval/__init__.py`
- `bca26c21e58161f0e3da8fdaf8049ef84771d934` Expose ranked ids in retrieval bundles
  Files: `THREAD_PACKET.md`, `docs/gate_passed.txt`, `src/qual/retrieval/service.py`
- `3ec7d52c97388827c0b09d891efca5b3522e7ddd` Harden FTS excerpt promotion metadata
  Files: `src/qual/retrieval/service.py`
- `24a5748f0fd6f6584bc2e96bfb7841006b214935` feat(retrieval): export canonical fts policy metadata
  Files: `src/qual/retrieval/__init__.py`
- `8548b765b46cec60d8eb0135786650175d0ed0c8` fix(retrieval): reject binary text inputs
  Files: `src/qual/engine/retrieval/fts_strategy.py`, `src/qual/retrieval/__init__.py`, `src/qual/retrieval/service.py`
- `39550c18399a5cba2ffad3e23e5b0d5078b416df` fix(retrieval): reject binary query metadata
  Files: `src/qual/retrieval/__init__.py`, `src/qual/retrieval/service.py`
- `49bf865572f9515875f57feffcd12bd312649502` Add demo-path field to review packets
  Files: `codex_packet_handoff/tools/init_lane_meta.py`, `codex_packet_handoff/tools/planner.py`, `tests/unit/test_packet_planner.py`
- `72a65689bc806e3f33afa9f28e87c827020e5021` fix(retrieval): normalize direct constraint booleans
  Files: `src/qual/retrieval/service.py`
- `b74c4330906db2bb660d96987ae4f75a0663cb4b` fix(packet): reconcile retrieval handoff ownership note
  Files: `THREAD_PACKET.md`, `codex_packet_handoff/tools/init_lane_meta.py`, `codex_packet_handoff/tools/planner.py`, `docs/gate_passed.txt`, `tests/unit/test_packet_planner.py`

## Metadata-Only Commits

- Commits: `c254197c42ba32f7deaf9a7894efc04832c9ed42`, `a0ab673c299430e2ecb0a68962554d13dadd6dba`, `f13324d206b41c134a96ff837eea6427c31aa981`, `edb36142cfe75ff8c65aee95865adb2de7ac19b0`, `b172559ed0889b5793e150296fa4b8b6c9943931`, `a164d042623b8d3fc52019c72c5be74bba18990b`, `3cc3dc84b80a8a1983d5ab90da1ef290ac6117fe`, `173ef4beac7ef361136d484c4d5e586424c13126`, `1435baa0fb0164b2972a512816fe680eb4710ee0`, `25f2ae42256307bdd306c5216d3cfce438d30c37`, `17177091b6e891f87d2aeb19887e5c4934070c93`, `93ea7d8749e73a663db2e75af274770e404c5d2c`, `221c6806eec977b9f7790094a58c5fc77d666827`, `be10c6b42d8aea5297c6db7da4c23ccb81185848`, `a0a58080f596fdf47783b5533e2f8cd9b27be067`, `a54d1824912cc75305acc7e96ad5ff2414d8001f`, `f7a2081d80db74f87db3ef97e11768a145b05db6`, `52f1a02f0bb908608335a2c721c09a0fb4ad4196`, `660605dfe7fe514db9cd1d81621aa49fb2e69813`, `8580681f7609bc792a0820d4ed884703e00cd6c1`, `6b3a5ea6594cef20706cf1cf87759810c44d9c31`, `fc5daa6729d2de8fb2d36975acc822f0ad00b23b`, `bbb9971681a6d3b62d765ccac711061e9f93dbd8`, `5d6ade670cd0323961b514451bfd834cd551d494`, `657f1f38f5a5fa9971aca032bc06d0649f27948e`, `1f4d32c935aae1e7f421d85a1601dc145914cf87`, `24d505735f5ff8655172cea8eebc949e3ced7f65`, `803cd2e92367324b326c83fc82e37e93fc8b6e6d`, `9d8f35af9e7ac87cdd8b554dc9eac9833f3a57fd`, `77a66517300c1bf9f3d0f7ae4ecba677569029c1`, `20440c427b5ace39e78d8a421ba65cf51078bb3b`, `9f7206fff61ca5738c5fb751ebc551fe43f6cdba`, `2efda180cdfdaf6b347aec8f8c95179ddb0c0a12`, `5665fb9f4f460918cdd33f1d914d5e7f948ba0c8`, `b271d2fe7135d9ea150df5fb15cedbb45eaa9d7d`, `4a7c4f1c31476afe92dcf89d4b19e9e93e5b7840`, `18f1a95eb9c4f45da1b32874c534209956449dc2`, `8d8371faa5801876887f430ee84230e8a5b6533b`, `1f6a57dd98e68ed3d2d831c03e673761ac343c80`, `dfd0dbea6d50a400c7d7b7c54f8348bc66f5177f`, `a9431c8b8b271c95adf00ab835ce3b6db4b41b19`, `1bcf17afaf14fe73184b20c3239d8e78a7f29413`, `2c9fafd3691cbf424037c3f9956fcd44c94abbed`, `67960f48cfff47df18ad91f3c9017a5f642fbad3`, `69bf513f82d171be2311358ab12e2c541c1df2d5`, `39a43890e3db7d5da81d8b703002e51f9ca888e4`, `77ac2140f039f4ff68b3993776f245472fa47126`, `646582c8495e1b891ee0eedab939a22e2d19d694`, `e1b75e1e720d156d5f9fe6949ece93f19f9db798`, `ab88c80e0ebf18848839e98729c3bae5b0eca94b`, `c0edeec541d7a9b03d59b80ff8e98d08081cbdf7`, `0a78066da152d81faa52b7b8214a439830ea64bf`, `39457eda47c1c4b8faad067272330adae89ff197`, `c83200b033f1b90a75700e3dc2f420e938057ca6`, `961714f2bc24e79c8df7133241e14fdef55a968e`, `f1608c3895048620c51585f4766cc897a022f237`, `60cc770ad9258f34f3625f3d8d9b26028c609390`, `63470717f54a00de11fae3e47c0b71985bc92c6e`, `a6a5a0075e3a0a5279e3f86801d5745830626a53`, `4246fc2582a92ace426a4635ad2e76be0eb72df5`, `d00822ca1945ff71c089d19198ae101a71b2f20e`, `029a9b6020b07fa9ee868ade261727f463ab337f`, `6bb18372fe58deaac25331aa0ddc5ad986dfe783`, `3da50128936519a8d3608ef831d67b3fd9d52888`, `b0629d0104c7569b541406ae1c3622fff7e90ced`, `86a59101b51dead580743dbd1d0465bef69da336`, `62478ac6cc29a445a04fb23c9890c787f6a2fb4d`, `f0e346d69e806af4cc9dced28f258fe57f76bab1`, `103de7cf5a14d7d284f63d993dfd8981ffbafdcf`, `1e5e83b325f798463fbfee0026c1815cc2388a3c`, `338955f577c5462c28bb738c26b4188fd24f610e`, `ceb51af02c94e9c3d92c363733dde62cc1fdac6b`, `0419fd3557526e797622031c2f58595c186a4fac`, `c4aace8148b6ec065c87befa6e4aacd413387cd5`, `87012554f71779763e5a5e76879d213b48282afd`, `bec55250b098b9a500846ba89690e5e52e492071`, `d2f02f019b5a38d79074ec871d2f284308abfe43`, `6d56213e70d29703520db916a3f8315a15e4cfe0`, `2d83344ec0535cd48d859522a6d8e25879a9cdc3`, `fa2ecdd70836d7c719124e16214e54be189c0d33`, `bc0154fc271a17d046780708655563758f2b947d`, `a391867c843944d703e73a6426d6c18dc3e57d0d`, `32e0b5a54c3e07c05b75d9e22f1acf86bf6795ea`, `c08047a93cf1872418455cb743cfbbee392347fa`, `5050d3e7fc8f138ba95236f9270d18363d88a2dc`, `73fb30956d80450ed98db6f843b0400afebcc233`, `19d7a725b26e3575eeaada9e2a72734b66a97205`, `ce6967d1c32baff0d60aba1b983affcdd7524375`, `287461d4b811d01efcd9e690ccd63362b773fe6b`, `2026498d8644e5f9f4f13c68e03c68443cb045e9`, `bba460f378584ed873358ad6010a9c9f9a3b08b0`, `061eaecee61f53424555028c38ae2bf4854f57ad`, `9f26474a2264b38735726bcf4460664a4016097d`, `34a0b21ac12d1ec607deb95de7d484e041f4d42d`, `3f3007e14a5bac33362689ac05e4a5f063fdaaf6`, `624409bac4b7805979931d9b8d0973e986580574`, `368eeb8afbf8e7763555d42dae18ba0d490031b5`, `c1e2e90a20e27f1f7044d707fdf162f36769c4e7`, `b187060980a84ead0b28c3e84d9554f760bfc1c6`, `e49646a9bdbbc7655a05b06bb1650dcdfb16ed70`, `4f6806826e75e96eaf61b55f57393519cbf8b7da`, `3b45b2cfbab4cee16e7d8dd71968499f56cc322d`, `6cf0aac81f36954bc60227ac4fe7e9a5557d06ab`, `b8a5522babd8f68548136c77321d4be3207e23d3`, `eec2b46ca1ab48fdda009e8a793b53c8e427aacb`, `e83486e92421967e9214044711b79ed5e7e84ca0`, `e56c2d53be1f7af9411c3cb0db6ee15dafa7266a`, `6226a64dce68eea1c43572c78066e810527a3a20`, `c8d33b4de18ad33fcd8bbf868c0dea96676b033b`, `5355a3fe39248df4b75e7ee36a8d506e6310225c`, `4f748884f6ac03f13559bde8ed1ba0ec9717816c`, `b14b0777d3a3b7e7eec41cd38b4f99a5b189c9d0`, `cf5363117376bb91b1707c7286f5301f9579be4d`, `56fba897fd0c6e545215a81e5afeec2d83207286`, `3595b8d83c8f8c6bb3572d41d78e76941b496434`, `84ba4821e7d29497d54c27d8dc143e03618a4a56`, `9ddf97669168a4d29eb87ef1abdee57961291712`, `f7812488a4e93b545242f8187f46677b80bbdcaf`, `75353fa460e741a3dcf3cc9ec106d4d39e71ccd9`, `5f57163e9753061e6c269234a215b725b12cedc8`, `b7793634efeb8133415e3b2a212957b694b70199`, `2c5549819808c2522ff338efc27713bc765c9dfb`, `1a9c960fa3bd7db1b512c7bd38955eb37b01365c`, `2e1ea42e73e9d7a4f029f1110cfaeaefd109e1ee`, `75a7f3775cd861bbdec835665bf7d9cc13792c06`, `4b0331ee770945443f870ba1eddf4d5df2d969e7`, `6a0c49177d59d288336fc207e1462a2eb61da43c`, `869cb7d39d97064317cb521683086cdb5c3eafba`, `b431058b81177277920b13542e9ab05a2d2b6924`, `6dff2fbbf3b3a798b30588f52d8b5575a853de9c`, `1c5f49284b98173954b2de4e5e0412303de24140`, `f03675eacc54a2cc7571cbdb6c62330cd337600a`, `f34e3fe75843be34a5c7b31102e603a21f2e3828`, `d1f919146d25587540137b18bb1be4cf72045bab`, `adf1fe69f16d3a5b4350d27ea70aa48bae3ca44d`, `4d81f80747cab5055cd400c357a1c96d6fb79c5c`, `ed825886845063dcf62ad713cc33dfaec4cdc612`, `9d6140bee17f4c3a882f3d12a732bbf1e979f91e`, `0e0dc8f0aa851bf429a1a75c04ebaa3806a541f5`, `9931e23b50bf6eb34062d0502d71c3c7004362e5`, `9c9605d133e1b02c4b58bac49197452d48dc4131`, `c2d272609564c27173e9691fe21afcdeb8008479`, `33e7fa3fb727112d45df9800b6ac22ad7a27224a`, `c1f4e05dd19fb7942e2d0ad59ff709f63c853076`, `9ed9df78755f3927a8ef0ac264e33c3cf30ba365`, `9e9b2c19a051ae3f192a98bf7aa975322951b393`, `0cf4746ff22117ade79d4d0d7919059cf7cabb38`, `199a95eff9a5ac433215622e3ced0189a206f406`, `c22a028ac069126a8d5f1c74448321132d0a615d`, `59fdca29ade0310d209c2302b8644b73d603f65d`, `14c5da55b55f5efe1cc7a2849d44db1516e14da6`, `857d085499ca7dd4aa5bbeef58589f3ae267ef6b`, `4b9110441565bab69e7368a6db31d589129a4611`, `6281ea8fcfae95e8a84f755b6d1d4add7e51ecc6`, `9a595c3b9bfc79f24cf4ca46a67bb0c8d2995c82`, `778eb5db8d5623d58a12051794ef720cb23ebd3a`, `9943e30e1957fa920ab1ac81e398fac152a68c87`, `856f6ccd78ca52a73d1a757e8bd7d922dcef4ab9`, `bccc788cb555029e699628b2bd1549d4d283e714`, `d6b7056cdc9316a73c3f79c1c083073bb92a71b9`, `b3d5fec4c88193583ce6cb28b67de6cbc621cc41`, `b008fe29758f55182ad0a704d26e8490605c5dbb`, `c85b5f2658e13a9d64e3c8c7f89bf49a99972c48`, `c6ab34e77e27f20d721a4f49d19575e232d2af47`, `da5e2db3e82921f1bcb33b4174a88a344bef41b4`, `249a0c507ac49ab93e711cf734307604433a5f25`, `0cf508e573af8ff1dc84fb37be65274331b7d22d`, `c163944c7cc8153d4760f432870ac882ec55612e`, `3848e7dc89c7c8097ce4e15ad0111a66770ad34d`, `a56545f2aa8800fef268ad00b468a99e849a0a5b`, `83fd8fec4800f353a1ea08dbbdc4d596b5f6812c`, `5fc2b29dec59f87050ec3c293e398ef490fa606e`, `00becda9e2d05badd2ed25d0073c81c24482aec8`, `7082d8a645db157ff298e74fb6fe32fcbb64a5dc`, `7fe156fcc30ed04baa36c053fd80ca3aa8c9671e`, `5ba8277e6be62cf7851281e1a95e951f51a65d45`, `2e81a359f3a651d7cea27ce543eafb0407867589`, `aaab9b3b00bcc4aa09c4ce564c57cebb811fcc13`, `c511415be829084b44e7136fac3a29b0707e3d4d`, `7d46c0bd0f602a9912e74b56cc984b10cba3bf58`, `d6cb6efc295834f7740e6c39f82f966cb3557e5b`, `8f16594e72a41fcca6d2ff8dbcfa91074bdaf8b6`, `8d7ef46e573f69653bd0c10568efa5ab46caca09`, `3e7a63b01f0bdf189a4744737b211f5a84a6602f`, `e6173aee8b6451c3b9b9c2ec5080bbf9d502c811`, `62b585baf894431fdb7b686dd333256c739978ec`, `f130c605a32172341932418d929ded0fc8b75cce`, `7b72ef7d0825591d3715570ae08a91998635cecc`, `8a27e618fd629df0624306ab5f5b3b4ac0f992e6`, `16650607619ecd3f2d96f339b523c8fad846373a`, `ddaf3fe2a74089100d49acfffbb27f55123c8d3f`, `1d975cf7851ab4d05b7cf699ef262776da7f57f7`, `368d802311f57964ffd9afc4b6956914a3d80e9d`, `c94831a1c72dd676053eac0b461aca62f8ec461f`, `b758f14149dab57e46e48301b52a7465c3e97845`, `b689336789ad8ed49034df17d828772828ac4456`, `d5f328a9cc6b43a4a10254f4418ac4d5a119f074`, `e25865c2fb93e64a1a5029426532897aab287346`, `79db0db5b82dbc836976ee22aa55651cfbcb0eb5`, `9918fb7ece3ae5523f43faef2c49df814374a00c`, `5ed3580d6096cb9b32acb5fd1114d2a901126cce`, `220762c791e3431466b4b23fc873b129fc9e40de`, `3fcb524f722349fd405b883fffbc5a078c981666`, `aa2176fa0ed323010033f4f93849c12d938a40ec`, `b1844019a8258c0f3d969843a09e26e4a7270d03`, `e4d7956110458f2d9e375d82c50e443b039a0571`, `bd170dac4927e920d546314a97cfe6a5c1e8bd45`, `e6d4aad59a855f4a18f4c004b21cd68b74117af9`, `6649f317c40d7a93bdb7238ec805c180daf4a29b`, `5832990212f463c854511ddb8ee1746e30018daf`, `2918379deb41cbf327dad0891d61acda5c401393`, `66c9dd844db34e66c9552f5dcf768f29bba94d00`, `ed1e6249ba85d0a11a517111766f2794b1a98127`, `6b62dbee31261416f53456d6d295664ab5d2c2c2`, `fce2e7c51faeafa5f413f6384bfdf4ec19f37b2d`, `7f7751585e61eab477b794687bb5c3524e6030ae`, `25b06dfeab27560be764c54c414c9c7680fe8941`, `f6c54946ae4021d3893e8fd25207a45aa6e03425`, `2e28b1b3a18045003a4c837b9177ec7fa6852e7e`, `26e7850909db06973a31f0a3bac2547a75474824`, `08bd422ed0ac30abb723b52e4b6ee8bb992461e6`, `69d462747782d6ccd9317d8bcea7c6d08493f249`, `656af71db316c2cd6e8ec31fa499634c32ce55d1`, `6c9d5a40c6eb999e4ecb2e00c4a74f4822e98581`, `69c8180f1903b2c5449bd391a8bd0a6e3b9c4f41`, `6630d8201599f9b3164a90e628cf90e66a211104`, `e6fe82bc73d3d7dfe22f6e97d6c7041aca76a5d7`, `be26f191d04f1fb84438cf03d323e9911bb72216`, `7202022777c3663f29de09545f345dc889a3478c`, `4dc8958d9014e9fded9d4023ebb9251602074e07`, `cb20e2fc02916f682caed819d2103d953d7fbccd`, `eff1e92e1c0f33205b1c647edd1423b3a32374a5`, `dccc7cbcd67e04ef0fcebf4f260fcbde8f2b8af9`, `3895d8a1ba501f920c0a3771554d155144949fe3`, `286ddb9ab3fb51276765081853cc816e9731f27a`, `9aa9540bb3f41b070b751dbf17c3bdbf210dc78b`, `2f0fb6f37822b6dca76578515304844b52f179a7`, `bebae3d23de3893f19e4611a949c59dc213e28c0`, `a6c62cdfb524b0ea70972535af3331cef4b2a728`, `d4d9c03aefbf3d606a3d1d3d85ebda54c3d05a15`, `5c38ec38720195392f5769208c68afca20697e6e`, `1764ebbdcf5a51316003dcd02171c4d1b402293c`, `970d4b4a0273d4cfcb660c6594bbd2244bacac5b`, `ad09cc1aad6b330171eb38344e8c07aae605c2e5`, `0e0684da73fe948e76a1724e1275b884ee1bbdf9`, `9531368a5429237ba6a7d7f282afea2f2f3e66bf`, `4ddabaceed89f7db4bd1d3eeaedc64462ce01d1a`, `62e46b154e86c3fb5673ac7798382e8ba9c53ae4`, `82ea62814b6263b4bcdfe378d90194cfb1a8a5b9`, `40875a5443dcf9ec9795f8f85567eb23503b3771`, `19395dfac8406e2d419307bb3006b9087443fb60`, `757d58dbacf11fcde631e45fcab6b3bea03933bb`, `8b0dcdabcb0a096e7c2f6641207499eec06960f0`, `4f23d84b24b99ecf56252d5942ae0960be4e3310`, `e408552613419c7b2ba310cd7c61e7035be9dc9b`, `b1a30c04cb244b16d06424ebfb94c213397699e9`, `55467c844c8c10e364cde39883444ccc8016336a`, `6dc9f7b9758d608e3916e9dfa4ebaeba3f5c0041`, `8f87d06eca587e49610188b8891875aeb8ee7df6`, `735c808347381be9059728e4bd4d97d071f2bfe4`, `d581bcbdab9e38bc45cf2b80d408425a1f675a11`, `e748b5f28cdd9fc511c5923eb37346ebfccf4d31`, `a7eb95f0f77e63e3f623edc49483066761e17106`, `5ec933efdd941ee999bc61b037376853fa4565ef`, `1392bc707554f6a38b97e40c0b20427a15f3a2b5`, `51cfe6d6275bb08f235a1898f26940ac67bd8983`, `0cc1e2506fc68e522a4b3f1c0bd7440d64715caa`, `ffd6986502683715ff5e83cc8a5d54fa5e3fe44b`, `83613da7058de1c91788afa42dd4b24734cf7bb4`, `f9716bb6ca28abccb8f2a39fdc00e2d5517b0c96`, `790c9174e79db53f0fb51e64d7e87d3a6a56ed31`, `485476f622d2857b6f1f3f8e9676aaccfd2bfd04`, `b48acb6207399beae634435ce67211d3ca489c86`, `5311edfbc5fe1a0ec90d55e9f47fabc636ecb81c`, `5669b5e595c965e13329cdc6b6e6f7aee4046c17`, `4ca63c1d5095b298f8e50669261eb99d6b5d8a13`, `29470e97c77b0060cae30789e41030db84e57d50`, `a96a162552f599aff2494092c732845eb424d737`, `12aa8ce1586ba8df8b8dae5de3b1c5ce0e6f453c`, `57af36012cfb2526b6312f64aff2980a988e1fef`, `c59f89132c1e24cacd4e8c5b0bfc6df0d5455cad`, `cda6b42e42fd0b1ff6330139150813d4796f2e5b`, `ec028af33381f142f87464297fd3ef3feedd2851`, `d6c36726221bf95d7d094632ac4344829e9f8979`, `ca4cfdedf85ba83d33cd18649708ed46e82b8af2`, `85d61f4510633e1d4bc74998fcf93308382b6e9c`, `a3419f04010c829d29d07eaf3ee0f7d6d0359d08`, `eab1d0e283abc1e4c80d38bb3282ff0b402444de`, `5d3a8c346aa956f8ece762038369821aecc208e5`, `6a911ab14054a3a976ed55a2072a432aa7174bf2`, `e867e335e4ef109319e657a64bbaa3b543d47e77`, `cace315f09fbd756a986acb5207760d5a885a8a4`, `8ac415f5cd738945fd8ac2e47339b0690922d3bb`, `47836150e4b9b048369903bd7c2293b999fc4b37`, `d1f3c54a9a58704c32f264ac138eeb6a2466e3a9`, `5955ea586aa3cb2fd8c8211e70758dc767971d69`, `115048df93c955f6fff28b46e5ade3f6b9df6054`, `8c8e4132cf03418eafa7a22f4a12e8839eb0253b`, `9e5345ee9b094f78a3d2fb2f9fdbd291d1bc496f`, `284331f266d0eba9bd9e97614ee4d42b6590cd98`, `85597a908e58a5391313db18ec76ce11dc02e3b2`, `c19c3870f7c0392ca00358bf186d8254fbb08382`, `1f3f30c3f0ba46c61c1fe29ab6065dd7cdb79ed5`, `ccd6412798fa90be2c8fd6e179cda82cdb03a4ce`, `b60fd538cde13f39f9192a75636fcd22b84aa7f6`, `d581530f312aa1b790b170bdf0194ddc16437943`, `cc3b6b6db917fe615c1e2a6930b3075ff99e82d3`, `a51808f8082b84bb3fc2eb53ad4e6c8b7bbe3a6d`, `b289015cf02ef726bc5dcd090711b4e21f1af929`, `a1ac2904a85f8833cc77c155e1b2a6d6750a3163`, `98afdd6fff84194f1dcd10b3698301c2e6cefe52`, `07fbd407f9cf425952a07531a2733f5a2ae850f0`, `926e36c9281b4b60cdf9fe4165ca825fd9a42daa`, `0745380c9350ea4758d20c4ce8a3458d5f79d893`, `8c9657d0b6c532a7b83116f8cdf24eb9f369b267`, `46c39db177cb95f2107d9475ab9c3eaeaaf793ed`, `78101d23b3fd532679d064d5c91e91acc9ffe814`, `aa4b458120e1cac33172368d633a0a85fa62763b`, `2ab1abbbf0a647b71989bcaca078cd88bff5ae4f`, `6ab81410b0d51d1525d18e3a9a5fb7006c99da6c`, `cfe1894e09ba8ba32ae7d073e7cffd35200e392e`, `5dbaee2a7304f54e024900e3520b97c56ab82936`, `6c19e8754c660465ac6c54ff4b12f0e28225caba`, `ae9c43f8c70b2ca3e5772ac1d8a7790e66fc2923`, `77834389cc7ee464bb3b2f5d48756afbd8f8af25`, `aeecaf7110c2ed2f59939ec11b29db44db7641aa`, `439328242b6f834f5a76ff234a8c41ff8f5f5c1a`, `a8c062b2268698de652f27e619ab30397d70d81a`, `7a5249a76698fd7865c3168176235d321d857c22`, `61f6cbde9b140ae0b30a96a8831c9b4392fc6da4`, `d4faefd3d56c63c0f7917cb1d49c3fa99f67ee34`, `b773d9afaa1703c08821e144e0ea3c3d300fdb10`, `19acbefebc3d487776103b88a7b157d931009a26`, `8588ad087b417e21e6925db25401f1733d9584ad`, `a450eeb1aee3701c4fc1b21c72565df20e46e2f4`, `70c83fbf82ac53e79e62d2095f0d3c24df7ee892`, `678c74435a59efba0a0cf0106409b85df8ba40c4`, `50b15f7823e0237ba0469a53194a84c0d63e4a1f`, `ce60aa2fa1d24280ffba6e3834f5e6924860b048`, `a5b9d337fab5a19275910625b7cc4d092bddff20`, `9347b964cd39433c748ed8534a9c4d26bbdb7d24`, `d6e372af4724c997940d79a6b87b800b91cbce97`, `b51345488ca378e5d2534b5b19759c05492dfe44`, `32b874cce8125ef551c741f1dc2f74c10c27a094`, `3e020cfc6a2c46c79d3a88d09b2aea66a76ea576`, `f237c6df3dbb34157131159fee9decbceff31c5c`, `a622df10a144e75b745200d60268cf7ee2e922b9`, `691d18c089c8ef618bfaa5d0dbc12bbcfd531725`, `e59fb0bcf6a02caf2a9869b569f3e6daafeb41e7`, `b42cb9520fbe9c15b39f8f9eee88ffbc65ef1f00`, `c639be3c7e792be677454a36416d560053242be4`, `be206340d37f26581ec2e8e9e3326e57a41587ef`, `7999d07e27b64c0fba34cac645b322772d25afef`, `ed2a6fcdc153aec47667f9173a35a224ba008db8`, `a8fa8be6a74f47d612464d0554f1fe1fa96e89f7`, `52681c01301d9717e8e69ae8bf8e86e53db51b1a`, `1d49b826bb808916ed6ef2f7b86db29aabf37f4e`, `66c783f1241ad835bed39bb3967543f46ca688c3`, `c0559e4d3aa689045bbc32a3b47f3daaaee97fed`, `3d9af86bc5210a7a95e8701fc0096832a073d4c6`, `25f7ded6feee8240dadf52c9f5b867419cf8ab76`, `8544c00092e1eff788bfc71ceed92871b16a6c3c`, `37690f6d63ee0418953d27a0e853e7dadb83610f`, `df2700ec7fbf22bcc15a3cd69ec239eaf8b3d45e`, `286443d7219b66428515eff3b3d6c0a63bc6a0d4`, `49df2e314c8905429f2841c0f8f4c07803db58e3`, `d27808265f8986df40d492ceb1a6832ace41f04f`, `ef056ad2aa89b6380f8538a82c55596dfe844404`, `305c401eb8a990928e4e121e85851ec88291af68`, `4c8597b9bda016e79d732464ba7e1ecc21131b62`, `b1b5541a5316b5064eddd27ac591406f4e2e8829`, `1e0ff5c05eabbb00854e8f677ee016fd317d9d34`, `fbbe0b17e46aa64d9a358af754a21c3f32b84d7d`, `29b3f602812e259ff9d24fa92710fd095f2bf3c4`, `e2612968f7a88cccfca1c82c825257b53fd50657`, `abe1d8a9f3f7df5ed0081139fbb345f4f1156845`, `079b5c5099de0386aaf931fe66739290dd733bb6`, `70f949e30ce1793c4a36696adb9512f85d8c73be`, `a3fc919e0c9b59f8b8ce0ed7ef8f0f6165db7edd`, `5c77799923c1308b980d99bba54be3a5c41778bd`, `b350b98840c7c7c2e166f9b5082ab307fe077295`, `194798db6c11bf8c2347a92fb802b5bb608dc9f1`, `ec40083d5b03433528cc4002d8ea457154d768c0`, `a3dfc0d1e84a97ad24227d3ef46fed803c038773`, `7314ebfac9486a7cffb661cf57b6553d31bc45b6`, `925b26f960c76c16c75d622ff26a3e39b3c7e019`, `eb87de7a6fa2138ac3314258339fc3aef5e664f0`, `bdd078e084fdcf4d8138a8e2b6727f1cc44e28f9`, `356167c980e7fedae72ad5a9329a467f99e5d647`, `d0e3f138efa3221e75484cb07b62f8f3b31ea7d9`, `bad798e66ef986f5b2814168b4d9ebc1f5eee3ed`, `49f09cd873b978c53bbb0819131979e6ead9eb5d`, `90882724e08a28232436b5764e5a282dbe8e5a47`, `0d7fcf4dbd14e597a69902ef7aad94a08d830f49`, `69dd2bc3ddc7c3c3e58d8162be7d75281d612408`, `092975c2ebd1ae61b93d32799ce54304a46929cd`, `ddd2fb4a2d9d1448160de6ee95b7d77809d952ce`, `223ac21e5cec90c01118f8a5a4bc1c2a7eb42099`, `a2960f00750d0ec3cfec803d682be40d096bcc80`, `f55d3e7d47c8bdaf8f85985b1d10f2042627d992`, `e5efd3f934be8164db6b2a8f01a9d425a94d0f24`, `8acec5e978ca3247e45bf95194a3beb0bec35958`, `64613ef6564142c909227ffd676e3cf035cd7f28`, `c19643341839bf7a310e0520702d0afcda80b1ef`, `cc19d850d7bb51b75ba88cfa11f39afca26ad579`, `8fa8f3e16d5181f9f0c134eed40bd540cbe41d14`, `14ccfddeb52c0890613e1a959565c617cbdd5dc7`, `0d0d474aa2dfc24b7b323884eb6e47b480deef72`, `c0158f6ee15270c214a3a8a47f9aa235446f6797`, `993b986716803f8e319b75c0983c46adcaf14302`, `36e68d83667bb0ab1b723560e0f8e0ef3698d17b`, `cd42fd6cca00530375312cf80c85adf63f3a05ba`, `bb3cd335f715909bf1827379e90509145980db5a`, `49adae867a897af667a611e4dd401eba63609280`, `55b702a014d789b1bdc74316496baa17dd14278c`, `211204a8ac29209a24367b7b9a95985186807958`, `132e1684eb25abef3d60ead7d1e488012ade7946`, `ad1cff2b91c60287de2b9dc7f43e92d8a0bb6d1a`, `16684eda08b7e88cf8f72015d78297d9ca44a60b`, `c5de93989da47b9f70098c2f0508a2c27a7fe576`, `29bce520675801793b820ed50def4da399bf1333`, `abe427f9080597ec61f42501149f9f360594424d`, `9afb6edbdd8743d3da70c41300df6d1fc0b7f2cf`, `c61042524920a5dfdd67293c6e82b0d713d23f4a`, `33c29df37784c7b19b2bca24334a69d8c867df98`, `8f99d4bbc116f359f589f64f9371b37d3dd8f153`, `235b9d24e41c880dba3acec7253fe980e7a2c5fb`, `3f010faf88f624075d206de7742a4aa060aaed74`, `8fd6086f684e78e68f1166ca4149a1a65424c81d`, `c2f6af279396db67f9588d72b9a92438f1eb2445`, `43d4667e6ac3364690be9fb857640944abf70b09`, `aa055ed38011d7f2817cf8a7ccd77bc636483257`, `d3dedf921e6e925deda71e72ec884d6db561441d`, `033ffcb22fb6d0693d41ab6e6a58c23f250b41be`, `2dd617613923b6d1a61e9ab9ce7cbd996b84ae18`, `49ac8c0e0317beb5cb41e1babfac93998c97d2f4`, `206e37e3509c1e3331b45258c6e82ab31e52a82e`, `2de3154c2cea415300ffe9a8aaf5335ffcf18350`, `15df1bfcb0aee45f4a9aa14e0c1a17d22977e740`, `412a3f777dcb7c1bb1ddf43e64b1fbce36d45982`, `ae97dc19919247096f568816d3b6d73eb6b3d022`, `aa1fa514439796bb96842fe60322d5cb935ee13c`, `0b6ed1990f38c492a31b8030dcce82fba74b6299`, `6e76ff4027ffb8c5d545644a60563f774224bfe9`, `81bf1a5edd1b85657399948f987508bb90f4f590`, `86e0f49aac171d1cfc4f461274c672233279cd64`, `30fea4b729a7401f98b1fff310e7b98e9e2d68c7`, `073c7701347fe6b7ded5c7f6ac58aff48cdbabee`, `782d6a5699dfa9e2d9017bcd5cf8e9ace8565b4e`, `87ce7b289ac62d4fdd37deaee2d3a8721c23ec6d`, `34b511ace9324f15de023d89e0b57bad382c35bd`, `1c2058975a5207bd7193a228bf8d0031f7d3e058`, `e8d55df788f164923a49d4fff284aa7390cafc75`, `cc3d60b554c44068cc41b980b125132d5d2bc665`, `39b1a1d5421b2d18b5a09aaaa3f517884da82672`, `4748167a2b68834ee90f430c072a8564b9f3bd45`, `3ce9b5d10defb43c8d180a73505804858614de60`, `057623be3ea8887e47c25debb4403247c4d94c9f`, `b3be6229cfd30c775252426de1b9d40780006542`, `572302f0cb9fe14df5657596dcdb3a9b6a2bea0c`, `14aec7fccac8c145358b007336f889a97d91636e`, `d9072b4e41615b9cba9ae4e08c874bb4c84a6557`, `61e4ac128985b8b36811eb9acf24a066e6987224`, `0e3ecf0425b89271de57bd381b743f1e289c70c5`, `25fe50aa948a518e7aae2feb66e080f86cee298f`, `0ce8d9c422792c6d097320f3f14013846362b86c`, `2bff8f1cefd16ad81464b891b8395cd4f431bfe7`, `ed9bb465de403d6c9f38a4a8fb04ed1dfcd4ddf8`, `216c73c4e5bb1a224fe825645823e5c316cd28a6`, `6d878e91e5b9ae623a962c373c37ec6edef64ca5`, `25bd27c155ac065c35e203031faf0b999a848a6f`, `7ec7e2720aee94c2b9c412fe1e003a4dc4fa6db4`, `e7e545664f277419ff97a05740e45f88179dbe24`, `48896bc54fc01250d865ff520a33776af5e15a71`, `5a979f53073a4b7d05c4acbe4803f1920cc3bbc9`, `302e264beff029792dd85fc5731f904b5950f8e9`, `57aa020dcd152d4910e49e66dd6293b3fecb166d`, `feff5ddd85ffee9db4679a4970ae4a73b3907df2`, `e139dab46d6e223cf5fa881b4ceeba9c35a8e013`, `e3ba89260c668280345b3ee0a55f2582823a522e`, `7df66af1eaa9947fde7a15d6173551124ab1fe8f`, `3f8890f52732ebf69d5159049faf52f16c57c3ef`, `efa8157ddd61614dfca0e65fad974b76d4fca10a`, `d72ff82f714ade900eeec67bfd2deee83cf1cf89`, `118c4f1dd0e008f5bf084678a0ffe00c091a1966`, `47804155ac0b2bcb58abe2b77a11b02d3604e798`, `c461c2adbdc3355ec2f8dae037e7110615102beb`, `53ede6e00cd9bf6bbf9e02531999d8e3f5c02528`, `1d2b68565bf0f0ade3b24d5b479fa2e47c9d250b`, `f8c949e1e3f40893aaefd53e188311d306c65050`, `36f958bf68c88e790f65ca2829ed7e18e6dee5f7`, `3627ab1ac6d86236919f76219644d8819d5bf925`, `96f4c08993cf6e9b7fab14a58b7b849a6b5936f9`, `9b5c1d678bdbadeab3587757dd656718e2eda681`, `40e8127dccc169c46d1c075786f582caa923f589`, `2ede039d39c079254a6088c1b7b9c07d87e4c54e`, `45dab6228bee7ceae0b9c62b10d8386d1a5bada7`, `f246061b66e00e2ad8e750c1b75a54cbcaae91b4`, `53e0926584689f0307eea64266ac56a0a05578be`, `0b954e5200ebf1553660b2ae3b8bf9fe02ace9b0`, `7af65c1b6353d98fd7a6b2f1f5715b92a116c1f2`, `b96b0941846164ba72d9549fa292d6b4bb0b9502`, `0beefa6afaf0634b279a394653b4b99e02144031`, `acdc03cbf88cceb1cd4f436c7d61987351ec8624`, `543a9afff9036e4201459d0e969a7188a4c46cf9`, `be93d7ff19212967a530137fda6c5ed35f9f096d`, `fbf51378aef9ce10428fd3fa91ccec13ff4ea17b`, `9fa8d5320f327f38bc88298c5cb37a76d74b833a`, `23b28e2f7386d8053cf22e91bda2d594611d218e`, `5824ddbba3f3880457bdfbab33d02c9a51557315`, `6ccd62dcb7d2073258d50f9a4882e786cab7e9d5`, `f5e71e451f0bd259b64cc1c722f373f3f13ecfb7`, `9f5388218211c3e3cc100845731545592393bedb`, `e0d146d4eb0ad4ec19a5d93f0b02a3a96da664c0`, `eee6ee24cb13a82057af40113fd98b2713c822a8`, `4e6a09c20298ae60ee258ce203d5dd1bfd4aa863`, `31b9110799ac606faa43c4c806be71cb0eddbce3`, `94a1fb6bd179b275992e02fd7be8938f4ff8fa1b`, `e1530c6809940ae74b931091eb5521b77cbba2f3`, `422d1fdabf53f56e70a26eb00fce31a15bc189f7`, `02f8944391bc1d78ff4b846a55c3dd39dd78b8bc`, `08cd31e30839f67cdaadb3d32e315d533b291210`, `ef827a8ad18ac6f2d70d5f80781f5a869acb9e4c`, `e013b29a1c7b099d8fb80b6a8b4d933fb279da41`, `61b9c36f4b42898c7f86440600d8e02ec34a0b2a`, `16a8f01386c3153974c09d8f781eeafbe3622504`, `cc22339c131fb30c3143edbb782f7cdf4dc3fdb7`, `6df9fd789ec7aa4e8301b1a7a9879b5f28bc2a7c`, `9f242d30d7a79bbbf7795c3d10218e360dc6136d`, `9bf6354eb5be984115d621aee698b172c9d498bd`, `7614905cdf5bb0c695423fce7915e54907462aa9`, `0c5666a28b46874f6b6e77692015ea561cf3ae75`, `059b68f366a2a67814e68f0baf9eb740600099bb`, `a0cdbb07e04243e3831b94cdb8f5625c73c70a06`, `c6098a890e05a9aeced98b94b06aaf1f9109bf3d`, `bb89109a53536665ec29dc235835bae288828cf2`, `f4ddf4d47dbe6ccc56d1c8739b8b9e1f31221c78`, `58474e0967272070e48febd42c29107e6000744b`, `d0d89fe51d8d44a0cc798698c7b0354c7392d307`, `57d07fe48d17e8527350dc48544f0f58f9b58409`, `cecfd1293fd882c97d263cab554e9cd955aff373`, `987053a811fd30cb43497814b058f9652310cc07`, `11c628efbad6e48468858c43f9280e8bf6db4d09`, `e96b9e841bca7609b37a168126eb982e8f352f49`, `04f5e07cea8089f17f6a7cae55b5f8a2a6ded41e`, `49729c7378ebe7d69e3c852559febe4f3d25b02f`, `df7829f8b8641af6b62eb839c41fb9c8db5a0cac`, `aeeb76a15fc99dc7597e296a61c5453e9676c628`, `6a0ba8e05618246f9735919b04d19ff37b5ae519`, `60948686e4b1dec6e159eef8925bf6204e31e65c`, `7baf6c00b331186a594ee71ed97aff846bbe7fe9`, `95cd919c67eb79d92374689a56e42b455bbbd5bf`, `a06a76dff54946419ea30c402cffac691a7da32b`, `764dc41208453059a2a8c96502a092b6676d4fd2`, `ca859a13eb27df76025cd4f4360273785a66fdec`, `8281cb5268963ddc73b09a4e0c9ddc4a4608efd7`, `f99d0ace1be84b3a7272b82b377fb4a164d0bf48`, `302d67a76d8cc4c761b6e94795e0bb19d324bb36`, `4302bc117bedba915197161c40f23c3a3537b373`, `1c726d425a34219a7729daface03258c2afdb52b`, `8a8640526d690f6a87e4728c238fef162444d7c2`, `df09450dbbd0eacddf303c77a5269c8b37c41dc4`, `f8162409cb057bc8797804abf9f003dfd1acb80c`, `e4cdc4ed19a1892bfcbb30765761a3f67c930773`, `e8c2e1d77d142ac48c39562661731b8e1f14049f`, `3140028f1635bd7d38d83aa8e7f42b8d07137aa5`, `1a6611118979d365d3b96d9d9cd51a715b30a9a4`, `0346eeec5d355bf3f27f9a00dcd086665413eb02`, `3a7f478b243e5e6e23c46a9bedea7f782defd497`, `dfc1b57b2dc95dfd8c99a4209c99cbdec10a9ac5`, `ac9d69d513a56a6414e0529dfa691e528bbf270a`, `97741987bea3d91d57c3acf96d0670748e740852`, `a80b002e8a79cae7b8032bcb7e74d6e17dd485cb`, `573f8e5685b33f957629a73d3362a80dd52e31bd`, `0b93738de77d77c557989af57a53e90dc5705a14`, `152cb4f1c5435250d5e3e31fe9054a93fe5efeb1`, `5882909d37c1ad7a2574f1f12082f58a544d46e1`, `dd73909afaeada2b8d48e7eade98f9a968636936`, `ac55a47429aeefc678ac26880ae8a0aaa7e885ed`, `aa12ab4713a175fa8da22ec7dc1710466e8e49cb`, `81e954da3f89e7b47b3adb3560d476fef87fdcba`, `fd974a1952c7829dc08147226cb8887ed43ebd5a`, `9ef1ea2aec30aded4968f844d48ab12226f27a1f`, `748004b1f28f30b1f662718ffc2d8c6960ebafe8`, `590104b90b25a2abad149c0eab14d93bf36cafe2`, `8f6fbb02309502159aac91a30d1fd6f0dcea114c`, `f360f73552fb5536abf9e4b74d1a8348fd54eec6`, `307c6576ecf36031ce7bee82f076580772e5ca77`, `f2c2cbd90bc3b5b5d062911296cb9b8d13a9c6d6`, `4eda66e82a1e705ddc6c99ab30df7a9c7484c723`, `82252a2079fe14ef3a99b952c0dae44fafe70e4f`, `3747013b2e1263fc27c0652c42f79ec45b34aba3`, `1ccf7cb10981166f9591beedb0e02738c20421dd`, `e60b5084b7a491066724b9524419f971d289b172`, `311de552886a977a2f7fc2959f963b664c746e1d`, `faed8f698cfea00bace723b1d8ec4bd36f7c152b`, `cfc97cf83cbe90bfabc4a0a182ce04538707a662`, `12dac04e4d4304ebb1bc8548474811991900cfd0`, `5afcc48bc7689668c2cf77fab7a110d1d7ca27e4`, `8daa4b59910410d2736a4584473dc9f03e2c3b42`, `48267f6e328b3f82e5ed9be7a45db55cbb9da3cf`, `31cb8a23788e9a4e435d8d365a82d5a520c54589`, `85430a5590d0f3f7387ae4bf9471f5ed4bf04272`, `9a80e25e4e30e9f559b2d64d74ab0c89d23fcf47`, `070c9dc460a0db4d9e409efe9b976fc98b9e8491`, `2a3426ea935cec1b7c287d2ca1cbacd694591388`, `38f160b01638dc8053dfbe27a1c1e34341a861ed`, `0038073fac1dfebef0c643769784c22f59bcbc92`, `d9dcf91cb19860de91d29d4e850312887d56c5e1`, `ab9a54d6ca4c076689e273f287925199fd0594c5`, `91017271631061ff5c6d76d32ac07bb168f21c28`, `314d8021abfee6f50e728f8c550f16ca7a2393cc`, `715824d4eacd6e614c834a0b773b223eb2bb9908`, `141b2168208d78cbd25bc8fd63fcdbc34e6aa958`, `986ef1e4f744590d05cd41d8d60577817e2f5731`, `592bce5fd33b69d7f83d0a020e39d25a2f75acf7`, `d0e0e7985de8549ea81831222e1543080a83cc65`, `76bb509bfe69429ab92d4401b033b8f173b082f6`, `b3b51e4ecae8301c2d8d492a871e9a75c3b6b29e`, `ddce27f96a0fd213608bb083ebe9478881537ad1`, `3365f4701f0df3e3b97a1ff18080e782fb7c9d1d`, `bdbf1eeaa4dcec296f17ad2f3639b18a37a3ea6d`, `147c000069281012f95a971f0f85ae3a30e09090`, `aaa8ffa9786fdd8e0d2d5eeda6608f0098ef797b`, `05c341b5acaa21bd64843e0ac1a6dc62bbed2d01`, `26395a2b80fac607b540cd9925284e9a51cf4c78`, `a418e1504ef358d2294541ef568587cd9d8e8d47`, `d5fdefca028c086e9da1743e4533197191a2e002`, `5aba2453ac09b1ed3a06b5d0a563d8526a7ac948`, `11441ef0f54f33a2adb128feb13ecf00555e2141`, `fc4c38684a4a09b5b7b90244d2117e688195aa00`, `6c4a28c2cb158e3fbe812021c9f547d85fa56ee1`, `6bd72d835d0e0df4a382b664cb97630447496758`, `e17805c6689edeebb9786c4c364992a0b5347602`, `23f67bb0be9beb036ab86eade9d48db62ea2dd21`, `fb511d91dc0e5b35c4f2e157b6f94bc9df16743c`, `620c6283ecb1cf51efeb170fc21e8237d16cdda5`, `dc803397d9190de7c2cc49d0e75a16a7f19629b3`, `cdf6ede6e9666729c33c0f68f5c8e726294f6415`, `a1f0dece6bdf8919b21508250333b09c2f17f31b`, `431e13ecd8b92e0bad1c701475c098c6e84db564`, `67cf9ec372b66c7e332efa310f8820f8f2824e61`, `b120016ba9ad21e1302740432848dd4273ee26a4`, `65b5cc92897fb5db223e3b9e69f44f16e91da015`, `a30809c13617516f67d63fed3a5e76c755085304`, `fdb3af1c404926722e7ba031fd270311ee496496`, `8f9cf40dc7f44a00d8f05c4692a0adb631cfc4f0`, `7a3ba74a22e3757a3e8c556d20599d0e2cbaa619`, `291e0a8c53ab8a5013c6d16d470bed0a8bba6c41`, `8a545525c6fbaa908a82d249d07c3cbb85cb7add`, `864d87926c820122269090f48052d7af7e4e8729`, `2e052094ccca6ce14c21e8dcb84cae195947c399`, `9256a923b209c25cc7fa15ade29750c2aab1c166`, `9a2a0446386e97673e215539562566b75f0f5c8b`, `65199b1a7bf57dd9a2c2fc15ba29c09402a7e7ff`, `53f86ec5caeed3350472dd0fb23cbc01de3aee79`, `f98446a00a6b9408f5aa8c378add473d099b0b5d`, `a14f5a1a40f49b2a3ef09f6524a70dde9d947085`, `116d268a4d5a9cb4a63e4621115e70f18ae1b203`, `84adb28957ee0ce5d24a76b516350ea5eb6deefe`, `ee2befa746328053cd9917307f87ae68ae3bc75e`, `c92c1f9a2e27d815594d5e090ee00811e2955304`, `6e759bbd066ac2a82e98e10faa7c82282a318d77`, `98e987e6199330d5161009a7aa1aa41f7e8bd2e9`, `2d3e45893fa22f719cb192315cf97be231cab491`, `f607320bd8242fef2050044dc25a47bbb96164c1`, `fb45c4398caa1ba620abcdf79395cc996117b625`, `ce9537056aabe397542c3eced0399ed497adc67c`, `5fda6f13c7e170dac8b3da37bf5e3d47c8516a4c`, `93ef4ebca9ea56681a0f185ebe90ce739e187c84`, `2988cbc50d8026c8c03776eb4ac67152eaa9bcab`, `12d0c10042f87bf23a692a0aa4e5d8d2bed91b74`, `d5d57e4ba3ee4be4da27e974263952bbf9d96829`, `cfdafc80691607d022746a315344d3961ab982cf`, `4ccdc82165bad7bcd8c96c0852244dd3ee8d5349`, `cc9c804c04e8771c1b99ffe847ebca4950d23e50`, `ac3414bccfaa246d7fc40c21c014769c18727494`, `b31db490a635fe5c7195cb2ce173b09a838ad8ab`, `51c55e3237fc8516ada15796f4c998a3ee3f8d3b`, `35c7fe709107d4d26567a29e0529f8a104d18cdb`
- Files touched across metadata-only commits:
  `.codex/kickoff_packets/feat-retrieval-fts.md`, `.codex/lane_meta/feat-retrieval-fts.json`, `THREAD_PACKET.md`
  `THREAD_PACKET.md`
  `docs/gate_passed.txt`
  `THREAD_PACKET.md`, `docs/gate_passed.txt`
