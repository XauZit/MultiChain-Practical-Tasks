# PHP 8 compatibility changes

This folder is [MultiChain/multichain-web-demo](https://github.com/MultiChain/multichain-web-demo) at
commit `582476bb3aeacd5e10c3c5807673725fec4a39a0` (2021-12-20), **modified on 2026-10-09 and 2026-10-10** so it runs on
PHP 8.x (tested with PHP 8.3.6 and 8.4.25). It remains under the GNU Affero General Public License,
see [LICENSE.txt](LICENSE.txt). Copyright (C) Coin Sciences Ltd.; modifications marked below.

The changes are applied by [`dev/php8_patch.py`](../dev/php8_patch.py) and only replace calls whose
behaviour changed in PHP 8:

| File(s) | Change | Why |
|---|---|---|
| `page-default.php`, `page-issue.php`, `page-update.php`, `page-streamfilter.php` | `count(@$x[...])` → `!empty($x[...])` | PHP 8 throws `TypeError` from `count(null)` (the `@` does not stop it), which crashed the Node page after **Get new address** and the Issue/Update pages once an asset existed |
| `functions.php` | `html()` casts null/scalars to string (arrays → JSON) | `htmlspecialchars(null)` is deprecated (8.1+); arrays throw `TypeError` |
| `functions.php`, `index.php`, `page-*.php` | `strlen($x)` → `strlen((string)$x)` where `$x` may be null; optional `$_POST[...]` fields read with `@` | Deprecation notices and "Undefined array key" warnings printed into the pages |
| `page-streamfilter.php`, `page-txfilter.php` | Unticked *Display callback results* checkboxes (`callbacks`, `sendcallbacks`, `rawcallbacks`) read with `@` | Testing a filter without ticking the box printed `Warning: Undefined array key` above the result |
| `functions.php` (`multichain_labels`) | Only hex labels are `pack('H*')`-decoded; `{"text":...}` items are used as-is; other items are ignored | Publishing a JSON/text item to the `root` stream produced warnings and garbled labels |

Everything else is unchanged.
