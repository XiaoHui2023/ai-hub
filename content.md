Index - Scrapling


[Skip to content](#top-sponsors)

[![logo](./assets/logo.png)](index.html "Scrapling")



Scrapling

Index





Search

[D4Vinci/Scrapling](https://github.com/D4Vinci/Scrapling "Go to repository")

[![logo](./assets/logo.png)](index.html "Scrapling")
Scrapling

[D4Vinci/Scrapling](https://github.com/D4Vinci/Scrapling "Go to repository")

* Introduction

  [Introduction](index.html)


  On this page
  + [Top Sponsors](#top-sponsors)
  + [Key Features](#key-features)

    - [Spiders — A Full Crawling Framework](#spiders-a-full-crawling-framework)
    - [Advanced Websites Fetching with Session Support](#advanced-websites-fetching-with-session-support)
    - [Adaptive Scraping & AI Integration](#adaptive-scraping-ai-integration)
    - [High-Performance & battle-tested Architecture](#high-performance-battle-tested-architecture)
    - [Developer/Web Scraper Friendly Experience](#developerweb-scraper-friendly-experience)
  + [Star History](#star-history)
  + [Installation](#installation)

    - [Optional Dependencies](#optional-dependencies)
    - [Docker](#docker)
  + [How the documentation is organized](#how-the-documentation-is-organized)
  + [Support](#support)
  + [License](#license)
* [Overview](./overview.html)
* [What's New in v0.3](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3)
* [What's New in v0.4](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4)
* [Performance Benchmarks](./benchmarks.html)
* User Guide



  User Guide
  + Parsing



    Parsing
    - [Querying elements](./parsing/selection.html)
    - [Main classes](./parsing/main_classes.html)
    - [Adaptive scraping](./parsing/adaptive.html)
  + Fetching



    Fetching
    - [Fetchers basics](./fetching/choosing.html)
    - [HTTP requests](./fetching/static.html)
    - [Dynamic websites](./fetching/dynamic.html)
    - [Dynamic websites with hard protections](./fetching/stealthy.html)
  + Spiders



    Spiders
    - [Architecture](./spiders/architecture.html)
    - [Getting started](./spiders/getting-started.html)
    - [Requests & Responses](./spiders/requests-responses.html)
    - [Sessions](./spiders/sessions.html)
    - [Proxy management & Blocking](./spiders/proxy-blocking.html)
    - [Advanced features](./spiders/advanced.html)
  + Command Line Interface



    Command Line Interface
    - [Overview](./cli/overview.html)
    - [Interactive shell](./cli/interactive-shell.html)
    - [Extract commands](./cli/extract-commands.html)
  + Integrations



    Integrations
    - [AI MCP server](./ai/mcp-server.html)
* Tutorials



  Tutorials
  + [A Free Alternative to AI for Robust Web Scraping](./tutorials/replacing_ai.html)
  + [Migrating from BeautifulSoup](./tutorials/migrating_from_beautifulsoup.html)
* Development



  Development
  + API Reference



    API Reference
    - [Selector](./api-reference/selector.html)
    - [Fetchers](./api-reference/fetchers.html)
    - [MCP Server](./api-reference/mcp-server.html)
    - [Custom Types](./api-reference/custom-types.html)
    - [Response](./api-reference/response.html)
    - [Spiders](./api-reference/spiders.html)
    - [Proxy Rotation](./api-reference/proxy-rotation.html)
  + [Writing your retrieval system](./development/adaptive_storage_system.html)
  + [Using Scrapling's custom types](./development/scrapling_custom_types.html)
* [Support and Advertisement](./donate.html)
* [Contributing](https://github.com/D4Vinci/Scrapling/blob/main/CONTRIBUTING.md)
* [Changelog](https://github.com/D4Vinci/Scrapling/releases)

On this page

* [Top Sponsors](#top-sponsors)
* [Key Features](#key-features)

  + [Spiders — A Full Crawling Framework](#spiders-a-full-crawling-framework)
  + [Advanced Websites Fetching with Session Support](#advanced-websites-fetching-with-session-support)
  + [Adaptive Scraping & AI Integration](#adaptive-scraping-ai-integration)
  + [High-Performance & battle-tested Architecture](#high-performance-battle-tested-architecture)
  + [Developer/Web Scraper Friendly Experience](#developerweb-scraper-friendly-experience)
* [Star History](#star-history)
* [Installation](#installation)

  + [Optional Dependencies](#optional-dependencies)
  + [Docker](#docker)
* [How the documentation is organized](#how-the-documentation-is-organized)
* [Support](#support)
* [License](#license)

Index
=====

[![Scrapling](assets/cover_light.svg)![Scrapling](assets/cover_dark.svg)](https://scrapling.readthedocs.io/en/latest/)

*Effortless Web Scraping for the Modern Web*
--------------------------------------------

Scrapling is an adaptive Web Scraping framework that handles everything from a single request to a full-scale crawl.

Its parser learns from website changes and automatically relocates your elements when pages update. Its fetchers bypass anti-bot systems like Cloudflare Turnstile out of the box. And its spider framework lets you scale up to concurrent, multi-session crawls with pause/resume and automatic proxy rotation — all in a few lines of Python. One library, zero compromises.

Blazing fast crawls with real-time stats and streaming. Built by Web Scrapers for Web Scrapers and regular users, there's something for everyone.

```
from scrapling.fetchers import Fetcher, StealthyFetcher, DynamicFetcher
StealthyFetcher.adaptive = True
page = StealthyFetcher.fetch('https://example.com', headless=True, network_idle=True)  # Fetch website under the radar!
products = page.css('.product', auto_save=True)                                        # Scrape data that survives website design changes!
products = page.css('.product', adaptive=True)                                         # Later, if the website structure changes, pass `adaptive=True` to find them!
```

Or scale up to full crawls

```
from scrapling.spiders import Spider, Response

class MySpider(Spider):
  name = "demo"
  start_urls = ["https://example.com/"]

  async def parse(self, response: Response):
      for item in response.css('.product'):
          yield {"title": item.css('h2::text').get()}

MySpider().start()
```

Top Sponsors[¶](#top-sponsors "Permanent link")
-----------------------------------------------

[![](https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/thordata.jpg)](https://www.thordata.com/?ls=github&lk=github "Unblockable proxies and scraping infrastructure, delivering real-time, reliable web data to power AI models and workflows.")
[![](https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/evomi.png)](https://evomi.com?utm_source=github&utm_medium=banner&utm_campaign=d4vinci-scrapling "Evomi is your Swiss Quality Proxy Provider, starting at $0.49/GB")
[![](https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/SerpApi.png)](https://serpapi.com/?utm_source=scrapling "Scrape Google and other search engines with SerpApi")
[![](https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/decodo.png)](https://visit.decodo.com/Dy6W0b "Try the Most Efficient Residential Proxies for Free")
[![](https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/petrosky.png)](https://petrosky.io/d4vinci "PetroSky delivers cutting-edge VPS hosting.")
[![](https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/hasdata.png)](https://hasdata.com/?utm_source=github&utm_medium=banner&utm_campaign=D4Vinci "The web scraping service that actually beats anti-bot systems!")
[![](https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/ProxyEmpire.png)](https://proxyempire.io/?ref=scrapling&utm_source=scrapling "Collect The Data Your Project Needs with the Best Residential Proxies")
[![](https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/HyperSolutions.png)](https://hypersolutions.co/?utm_source=github&utm_medium=readme&utm_campaign=scrapling "Bot Protection Bypass API for Akamai, DataDome, Incapsula & Kasada")

*Do you want to show your ad here? Click [here](https://github.com/sponsors/D4Vinci/sponsorships?tier_id=435495) and enjoy the rest of the perks!*

Key Features[¶](#key-features "Permanent link")
-----------------------------------------------

### Spiders — A Full Crawling Framework[¶](#spiders-a-full-crawling-framework "Permanent link")

* 🕷️ **Scrapy-like Spider API**: Define spiders with `start_urls`, async `parse` callbacks, and `Request`/`Response` objects.
* ⚡ **Concurrent Crawling**: Configurable concurrency limits, per-domain throttling, and download delays.
* 🔄 **Multi-Session Support**: Unified interface for HTTP requests, and stealthy headless browsers in a single spider — route requests to different sessions by ID.
* 💾 **Pause & Resume**: Checkpoint-based crawl persistence. Press Ctrl+C for a graceful shutdown; restart to resume from where you left off.
* 📡 **Streaming Mode**: Stream scraped items as they arrive via `async for item in spider.stream()` with real-time stats — ideal for UI, pipelines, and long-running crawls.
* 🛡️ **Blocked Request Detection**: Automatic detection and retry of blocked requests with customizable logic.
* 📦 **Built-in Export**: Export results through hooks and your own pipeline or the built-in JSON/JSONL with `result.items.to_json()` / `result.items.to_jsonl()` respectively.

### Advanced Websites Fetching with Session Support[¶](#advanced-websites-fetching-with-session-support "Permanent link")

* **HTTP Requests**: Fast and stealthy HTTP requests with the `Fetcher` class. Can impersonate browsers' TLS fingerprint, headers, and use HTTP/3.
* **Dynamic Loading**: Fetch dynamic websites with full browser automation through the `DynamicFetcher` class supporting Playwright's Chromium and Google's Chrome.
* **Anti-bot Bypass**: Advanced stealth capabilities with `StealthyFetcher` and fingerprint spoofing. Can easily bypass all types of Cloudflare's Turnstile/Interstitial with automation.
* **Session Management**: Persistent session support with `FetcherSession`, `StealthySession`, and `DynamicSession` classes for cookie and state management across requests.
* **Proxy Rotation**: Built-in `ProxyRotator` with cyclic or custom rotation strategies across all session types, plus per-request proxy overrides.
* **Domain Blocking**: Block requests to specific domains (and their subdomains) in browser-based fetchers.
* **Async Support**: Complete async support across all fetchers and dedicated async session classes.

### Adaptive Scraping & AI Integration[¶](#adaptive-scraping-ai-integration "Permanent link")

* 🔄 **Smart Element Tracking**: Relocate elements after website changes using intelligent similarity algorithms.
* 🎯 **Smart Flexible Selection**: CSS selectors, XPath selectors, filter-based search, text search, regex search, and more.
* 🔍 **Find Similar Elements**: Automatically locate elements similar to found elements.
* 🤖 **MCP Server to be used with AI**: Built-in MCP server for AI-assisted Web Scraping and data extraction. The MCP server features powerful, custom capabilities that leverage Scrapling to extract targeted content before passing it to the AI (Claude/Cursor/etc), thereby speeding up operations and reducing costs by minimizing token usage. ([demo video](https://www.youtube.com/watch?v=qyFk3ZNwOxE))

### High-Performance & battle-tested Architecture[¶](#high-performance-battle-tested-architecture "Permanent link")

* 🚀 **Lightning Fast**: Optimized performance outperforming most Python scraping libraries.
* 🔋 **Memory Efficient**: Optimized data structures and lazy loading for a minimal memory footprint.
* ⚡ **Fast JSON Serialization**: 10x faster than the standard library.
* 🏗️ **Battle tested**: Not only does Scrapling have 92% test coverage and full type hints coverage, but it has been used daily by hundreds of Web Scrapers over the past year.

### Developer/Web Scraper Friendly Experience[¶](#developerweb-scraper-friendly-experience "Permanent link")

* 🎯 **Interactive Web Scraping Shell**: Optional built-in IPython shell with Scrapling integration, shortcuts, and new tools to speed up Web Scraping scripts development, like converting curl requests to Scrapling requests and viewing requests results in your browser.
* 🚀 **Use it directly from the Terminal**: Optionally, you can use Scrapling to scrape a URL without writing a single line of code!
* 🛠️ **Rich Navigation API**: Advanced DOM traversal with parent, sibling, and child navigation methods.
* 🧬 **Enhanced Text Processing**: Built-in regex, cleaning methods, and optimized string operations.
* 📝 **Auto Selector Generation**: Generate robust CSS/XPath selectors for any element.
* 🔌 **Familiar API**: Similar to Scrapy/BeautifulSoup with the same pseudo-elements used in Scrapy/Parsel.
* 📘 **Complete Type Coverage**: Full type hints for excellent IDE support and code completion. The entire codebase is automatically scanned with **PyRight** and **MyPy** with each change.
* 🔋 **Ready Docker image**: With each release, a Docker image containing all browsers is automatically built and pushed.

Star History[¶](#star-history "Permanent link")
-----------------------------------------------

Scrapling’s GitHub stars have grown steadily since its release (see chart below).

[![Star History Chart](https://api.star-history.com/svg?repos=D4Vinci/Scrapling&type=Date)](https://github.com/D4Vinci/Scrapling)

Installation[¶](#installation "Permanent link")
-----------------------------------------------

Scrapling requires Python 3.10 or higher:

```
pip install scrapling
```

This installation only includes the parser engine and its dependencies, without any fetchers or commandline dependencies.

### Optional Dependencies[¶](#optional-dependencies "Permanent link")

1. If you are going to use any of the extra features below, the fetchers, or their classes, you will need to install fetchers' dependencies and their browser dependencies as follows:

   ```
   pip install "scrapling[fetchers]"

   scrapling install           # normal install
   scrapling install  --force  # force reinstall
   ```

   This downloads all browsers, along with their system dependencies and fingerprint manipulation dependencies.

   Or you can install them from the code instead of running a command like this:

   ```
   from scrapling.cli import install

   install([], standalone_mode=False)          # normal install
   install(["--force"], standalone_mode=False) # force reinstall
   ```
2. Extra features:

   * Install the MCP server feature:

     ```
     pip install "scrapling[ai]"
     ```
   * Install shell features (Web Scraping shell and the `extract` command):

     ```
     pip install "scrapling[shell]"
     ```
   * Install everything:

     ```
     pip install "scrapling[all]"
     ```

     Don't forget that you need to install the browser dependencies with `scrapling install` after any of these extras (if you didn't already)

### Docker[¶](#docker "Permanent link")

You can also install a Docker image with all extras and browsers with the following command from DockerHub:

```
docker pull pyd4vinci/scrapling
```

Or download it from the GitHub registry:

```
docker pull ghcr.io/d4vinci/scrapling:latest
```

This image is automatically built and pushed using GitHub Actions and the repository's main branch.

How the documentation is organized[¶](#how-the-documentation-is-organized "Permanent link")
-------------------------------------------------------------------------------------------

Scrapling has extensive documentation, so we try to follow the [Diátaxis documentation framework](https://diataxis.fr/).

Support[¶](#support "Permanent link")
-------------------------------------

If you like Scrapling and want to support its development:

* ⭐ Star the [GitHub repository](https://github.com/D4Vinci/Scrapling)
* 🚀 Follow us on [Twitter](https://x.com/Scrapling_dev) and join the [discord server](https://discord.gg/EMgGbDceNQ)
* 💝 Consider [sponsoring the project or buying me a coffee](donate.html) ![😉](https://cdn.jsdelivr.net/gh/jdecked/twemoji@16.0.1/assets/svg/1f609.svg ":wink:")
* 🐛 Report bugs and suggest features through [GitHub Issues](https://github.com/D4Vinci/Scrapling/issues)

License[¶](#license "Permanent link")
-------------------------------------

This project is licensed under the BSD-3 License. See the [LICENSE](https://github.com/D4Vinci/Scrapling/blob/main/LICENSE) file for details.

Was this page helpful?

Thanks for your feedback!

Thanks for your feedback! Help us improve this page by
[opening a documentation issue](https://github.com/D4Vinci/Scrapling/issues/new?template=04-docs_issue.yml).

Back to top
[Next

Overview](./overview.html)

Copyright © 2025 Karim Shoair - [Change cookie settings](#__consent)

Made with
[Zensical](https://zensical.org/)

#### Cookie consent

We use cookies to recognize your repeated visits and preferences, as well
as to measure the effectiveness of our documentation and whether users
find what they're searching for. With your consent, you're helping us to
make our documentation better.

* Google Analytics
* GitHub

Accept
Reject
Manage settings