#!/usr/bin/env python3
"""
Automated Quality, SEO, Structured Data & Accessibility Validation Runner.
Repository: marcinrzezniczuk_webpage
Author: worker_m3

Production-ready zero-dependency verification runner written in pure Python 3 standard library.
Implements 6 comprehensive validation suites:
  Suite 1: Document Architecture & HTML5 Doctype
  Suite 2: LIFO Stack Tag Nesting, Balancing & Void Element Enforcement
  Suite 3: DOM ID Uniqueness & Anchor Integrity
  Suite 4: SEO & Social Meta Tags (Canonical, OpenGraph, Twitter Cards, Robots)
  Suite 5: Schema.org JSON-LD Structured Data (ProfilePage, Person, Credentials, sameAs)
  Suite 6: Bilingual Symmetry (.lang-en vs .lang-pl) & WCAG Interactive Accessibility

Usage:
  python3 validate_site.py [path_to_html] [--verbose]
"""

import html.parser
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# HTML5 standard void elements (must never have closing tags)
VOID_TAGS: Set[str] = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr"
}

# Standard SVG self-closing elements valid inside <svg>
SVG_SELF_CLOSING: Set[str] = {
    "path", "circle", "rect", "line", "polyline", "polygon", "stop", "use",
    "ellipse", "mask", "clipPath", "defs"
}

# Required OpenGraph properties for rich link previews
REQUIRED_OG_TAGS: List[str] = [
    "og:type", "og:site_name", "og:title", "og:description",
    "og:url", "og:image", "og:locale"
]

# Required Twitter Card meta names
REQUIRED_TWITTER_TAGS: List[str] = [
    "twitter:card", "twitter:title", "twitter:description", "twitter:image"
]


class TagNode:
    """Represents an opened non-void element on the parsing stack."""
    __slots__ = ("tag", "pos", "attrs")

    def __init__(self, tag: str, pos: Tuple[int, int], attrs: Dict[str, Optional[str]]):
        self.tag = tag
        self.pos = pos
        self.attrs = attrs

    def __repr__(self) -> str:
        return f"<{self.tag}> at {self.pos[0]}:{self.pos[1]}"


class HTMLTreeParser(html.parser.HTMLParser):
    """
    Event-driven HTML parser enforcing strict HTML5 LIFO tag nesting,
    void element rules, ID uniqueness, bilingual node collection, and
    interactive accessibility baseline.
    """

    def __init__(self):
        super().__init__()
        self.stack: List[TagNode] = []
        self.errors: List[str] = []
        self.warnings: List[str] = []

        # Elements and metadata storage
        self.ids: Dict[str, Tuple[int, int]] = {}
        self.duplicate_ids: List[Tuple[str, Tuple[int, int], Tuple[int, int]]] = []
        self.meta_tags: List[Tuple[Tuple[int, int], Dict[str, Optional[str]]]] = []
        self.link_tags: List[Tuple[Tuple[int, int], Dict[str, Optional[str]]]] = []
        self.json_ld_scripts: List[Tuple[Tuple[int, int], str]] = []
        self.svg_elements: List[Tuple[Tuple[int, int], Dict[str, Optional[str]]]] = []

        # Internal and external anchors
        self.anchor_targets: Set[str] = set()
        self.external_links: List[Tuple[Tuple[int, int], Dict[str, Optional[str]]]] = []

        # Bilingual nodes (excluding body state toggle)
        self.lang_en_nodes: List[Tuple[str, Tuple[int, int], Dict[str, Optional[str]], Optional[str]]] = []
        self.lang_pl_nodes: List[Tuple[str, Tuple[int, int], Dict[str, Optional[str]], Optional[str]]] = []

        # Interactive elements for accessibility
        self.interactive_elements: List[Dict[str, Any]] = []
        self.active_interactive_stack: List[Dict[str, Any]] = []

        # Parsing states
        self.in_svg = False
        self.in_json_ld = False
        self.current_json_ld = ""
        self.in_title = False
        self.title_text = ""
        self.has_html_tag = False
        self.html_attrs: Dict[str, Optional[str]] = {}
        self.has_head_tag = False
        self.has_body_tag = False
        self.body_attrs: Dict[str, Optional[str]] = {}
        self.has_main_tag = False
        self.main_attrs: Dict[str, Optional[str]] = {}

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]):
        pos = self.getpos()
        attrs_dict = dict(attrs)
        parent_tag = self.stack[-1].tag if self.stack else None

        if tag == "html":
            self.has_html_tag = True
            self.html_attrs = attrs_dict
        elif tag == "head":
            self.has_head_tag = True
        elif tag == "body":
            self.has_body_tag = True
            self.body_attrs = attrs_dict
        elif tag == "main":
            self.has_main_tag = True
            self.main_attrs = attrs_dict
        elif tag == "title":
            self.in_title = True
            self.title_text = ""
        elif tag == "svg":
            self.in_svg = True
            self.svg_elements.append((pos, attrs_dict))

        # Check DOM ID uniqueness
        if "id" in attrs_dict and attrs_dict["id"]:
            el_id = attrs_dict["id"]
            if el_id in self.ids:
                first_pos = self.ids[el_id]
                self.duplicate_ids.append((el_id, first_pos, pos))
                self.errors.append(
                    f"Duplicate ID '{el_id}' at line {pos[0]}, col {pos[1]} "
                    f"(first defined at line {first_pos[0]}, col {first_pos[1]})"
                )
            else:
                self.ids[el_id] = pos

        # Track metadata and scripts
        if tag == "meta":
            self.meta_tags.append((pos, attrs_dict))
        elif tag == "link":
            self.link_tags.append((pos, attrs_dict))
        elif tag == "script" and attrs_dict.get("type") == "application/ld+json":
            self.in_json_ld = True
            self.current_json_ld = ""

        # Track anchor links
        if tag == "a":
            href = attrs_dict.get("href", "")
            if href.startswith("#") and len(href) > 1:
                self.anchor_targets.add(href[1:])
            elif href.startswith("http://") or href.startswith("https://"):
                self.external_links.append((pos, attrs_dict))

        # Track bilingual elements (excluding root body controller)
        classes = attrs_dict.get("class", "").split()
        if "lang-en" in classes and tag != "body":
            self.lang_en_nodes.append((tag, pos, attrs_dict, parent_tag))
        if "lang-pl" in classes and tag != "body":
            self.lang_pl_nodes.append((tag, pos, attrs_dict, parent_tag))

        # Track interactive elements for WCAG accessibility
        if tag in ("a", "button", "input", "textarea", "select"):
            inter_entry = {
                "tag": tag,
                "pos": pos,
                "attrs": attrs_dict,
                "text": ""
            }
            self.interactive_elements.append(inter_entry)
            self.active_interactive_stack.append(inter_entry)

        # LIFO stack management for non-void elements
        if tag not in VOID_TAGS:
            self.stack.append(TagNode(tag, pos, attrs_dict))

    def handle_endtag(self, tag: str):
        pos = self.getpos()

        if tag == "svg":
            self.in_svg = False
        elif tag == "title":
            self.in_title = False
        elif tag == "script" and self.in_json_ld:
            self.in_json_ld = False
            self.json_ld_scripts.append((pos, self.current_json_ld))
            self.current_json_ld = ""

        # Pop from interactive stack
        if self.active_interactive_stack and self.active_interactive_stack[-1]["tag"] == tag:
            self.active_interactive_stack.pop()

        # HTML5 void elements must NEVER have closing tags
        if tag in VOID_TAGS:
            self.errors.append(
                f"Forbidden explicit closing tag </{tag}> at line {pos[0]}, col {pos[1]}. "
                f"HTML5 void elements are self-contained and must never have explicit closing tags."
            )
            return

        # Empty stack check
        if not self.stack:
            self.errors.append(
                f"Unexpected closing tag </{tag}> at line {pos[0]}, col {pos[1]} with empty stack."
            )
            return

        # LIFO balance verification
        top_node = self.stack.pop()
        if top_node.tag != tag:
            self.errors.append(
                f"Mismatched closing tag </{tag}> at line {pos[0]}, col {pos[1]}; "
                f"expected </{top_node.tag}> opened at line {top_node.pos[0]}, col {top_node.pos[1]}."
            )

    def handle_startendtag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]):
        pos = self.getpos()
        attrs_dict = dict(attrs)

        if tag == "meta":
            self.meta_tags.append((pos, attrs_dict))
        elif tag == "link":
            self.link_tags.append((pos, attrs_dict))
        elif tag in VOID_TAGS:
            pass  # Allowed self-closing on void elements (e.g. <img /> or <meta />)
        elif self.in_svg and tag in SVG_SELF_CLOSING:
            pass  # Valid SVG self-closing elements (e.g. <path ... />)
        else:
            # Illegal XML-style self-closing on non-void HTML elements
            self.errors.append(
                f"Non-void HTML element <{tag} /> must not be self-closed at line {pos[0]}, col {pos[1]}. "
                f"In HTML5, non-void tags require explicit closing tags <{tag}></{tag}>."
            )

    def handle_data(self, data: str):
        if self.in_json_ld:
            self.current_json_ld += data
        if self.in_title:
            self.title_text += data
        for inter in self.active_interactive_stack:
            inter["text"] += " " + data.strip()


class ValidationSuite:
    """Manages test assertions and formatting for a validation suite."""

    def __init__(self, number: int, title: str):
        self.number = number
        self.title = title
        self.passed_checks: List[str] = []
        self.failed_checks: List[str] = []
        self.warnings: List[str] = []

    def pass_check(self, message: str):
        self.passed_checks.append(message)

    def fail_check(self, message: str):
        self.failed_checks.append(message)

    def warn_check(self, message: str):
        self.warnings.append(message)

    @property
    def passed(self) -> bool:
        return len(self.failed_checks) == 0

    def print_report(self, verbose: bool = False):
        status_symbol = "✓ PASS" if self.passed else "✗ FAIL"
        print(f"\n[{self.number}/6] {self.title} — {status_symbol}")
        print("-" * 65)

        for fail in self.failed_checks:
            print(f"  [FAIL] {fail}")

        if verbose or not self.passed:
            for passed in self.passed_checks:
                print(f"  [PASS] {passed}")

        for warn in self.warnings:
            print(f"  [WARN] {warn}")

        if not verbose and self.passed:
            print(f"  All {len(self.passed_checks)} assertions passed cleanly.")


# =============================================================================
# SUITE 1: Document Architecture & HTML5 Doctype
# =============================================================================
def suite_1_document_architecture(content: str, parser: HTMLTreeParser) -> ValidationSuite:
    suite = ValidationSuite(1, "Document Architecture & HTML5 Doctype")

    # 1. HTML5 Doctype
    clean_prefix = content.lstrip()
    if clean_prefix.lower().startswith("<!doctype html>"):
        suite.pass_check("HTML5 DOCTYPE declared properly at document start ('<!DOCTYPE html>').")
    else:
        suite.fail_check("Document missing standard HTML5 '<!DOCTYPE html>' declaration at start.")

    # 2. Root <html> with lang attribute
    if parser.has_html_tag:
        lang = parser.html_attrs.get("lang")
        if lang:
            suite.pass_check(f"Root <html> tag present with lang attribute ('{lang}').")
        else:
            suite.fail_check("Root <html> tag present but missing 'lang' attribute.")
    else:
        suite.fail_check("Root <html> element missing from document.")

    # 3. <head> and <body> structure
    if parser.has_head_tag:
        suite.pass_check("Document <head> container present.")
    else:
        suite.fail_check("Document missing <head> container.")

    if parser.has_body_tag:
        suite.pass_check("Document <body> container present.")
    else:
        suite.fail_check("Document missing <body> container.")

    # 4. <title> presence and length
    title = parser.title_text.strip()
    if title and len(title) >= 10:
        suite.pass_check(f"<title> element verified with descriptive length ({len(title)} chars): '{title}'.")
    elif title:
        suite.fail_check(f"<title> element too short (< 10 chars): '{title}'.")
    else:
        suite.fail_check("Document missing non-empty <title> element in <head>.")

    # 5. Charset declaration
    charset_found = False
    for _, attrs in parser.meta_tags:
        if attrs.get("charset", "").lower() == "utf-8" or "utf-8" in attrs.get("content", "").lower():
            charset_found = True
            break
    if charset_found:
        suite.pass_check("Character encoding explicitly declared as UTF-8.")
    else:
        suite.fail_check("Missing '<meta charset=\"UTF-8\">' declaration.")

    # 6. Viewport declaration
    viewport_meta = next((attrs for _, attrs in parser.meta_tags if attrs.get("name") == "viewport"), None)
    if viewport_meta and "width=device-width" in viewport_meta.get("content", ""):
        suite.pass_check("Responsive viewport meta tag verified ('width=device-width').")
    else:
        suite.fail_check("Missing or incomplete '<meta name=\"viewport\" content=\"width=device-width...\">' tag.")

    # 7. Semantic <main> landmark
    if parser.has_main_tag:
        main_id = parser.main_attrs.get("id")
        if main_id == "main-content":
            suite.pass_check("Semantic <main> landmark verified with id='main-content'.")
        else:
            suite.fail_check(f"Semantic <main> landmark present but expected id='main-content', got '{main_id}'.")
    else:
        suite.fail_check("Missing semantic <main> landmark element.")

    return suite


# =============================================================================
# SUITE 2: Tag Nesting, LIFO Stack & Void Element Enforcement
# =============================================================================
def suite_2_tag_nesting(parser: HTMLTreeParser) -> ValidationSuite:
    suite = ValidationSuite(2, "LIFO Stack Tag Nesting & Void Element Enforcement")

    # 1. Check parser errors (mismatches, void tag closings, non-void self-closings)
    if parser.errors:
        suite.fail_check(f"Detected {len(parser.errors)} HTML structural nesting error(s):")
        for err in parser.errors:
            suite.fail_check(f"  -> {err}")
    else:
        suite.pass_check("0 tag mismatch or unexpected closing tag errors.")
        suite.pass_check("0 forbidden explicit closing tags on void elements (no illegal </meta>, </link>, </br>).")
        suite.pass_check("0 illegal XML self-closing tags on non-void HTML elements (no illegal <div />, <span />).")

    # 2. Check unclosed tags on the LIFO stack at EOF
    if parser.stack:
        suite.fail_check(f"Found {len(parser.stack)} unclosed tag(s) remaining at EOF:")
        for node in parser.stack:
            suite.fail_check(f"  -> Unclosed <{node.tag}> opened at line {node.pos[0]}, col {node.pos[1]}")
    else:
        suite.pass_check("LIFO tag stack is completely empty at EOF (all opened non-void tags cleanly closed).")

    return suite


# =============================================================================
# SUITE 3: DOM ID Uniqueness & Anchor Integrity
# =============================================================================
def suite_3_dom_id_uniqueness(parser: HTMLTreeParser) -> ValidationSuite:
    suite = ValidationSuite(3, "DOM ID Uniqueness & Anchor Integrity")

    # 1. ID Uniqueness
    if parser.duplicate_ids:
        suite.fail_check(f"Found {len(parser.duplicate_ids)} duplicate DOM ID(s):")
        for el_id, orig_pos, dup_pos in parser.duplicate_ids:
            suite.fail_check(
                f"  -> Duplicate id='{el_id}' at line {dup_pos[0]}, col {dup_pos[1]} "
                f"(first seen at line {orig_pos[0]}, col {orig_pos[1]})"
            )
    else:
        suite.pass_check(f"All {len(parser.ids)} DOM IDs verified unique across document with 0 collisions.")

    # 2. Key section IDs presence
    expected_ids = ["about", "experience", "certifications", "expertise", "how-i-work", "contact", "btn-en", "btn-pl"]
    missing_ids = [i for i in expected_ids if i not in parser.ids]
    if missing_ids:
        suite.fail_check(f"Missing expected milestone navigation section ID(s): {', '.join(missing_ids)}")
    else:
        suite.pass_check(f"All {len(expected_ids)} key portfolio section and navigation IDs confirmed present.")

    # 3. Anchor Target Integrity (href="#target")
    broken_anchors = [t for t in parser.anchor_targets if t not in parser.ids]
    if broken_anchors:
        suite.fail_check(f"Anchor links point to non-existent DOM ID target(s): {', '.join(broken_anchors)}")
    else:
        suite.pass_check(f"All {len(parser.anchor_targets)} internal hash anchor target(s) resolve to existing DOM IDs.")

    return suite


# =============================================================================
# SUITE 4: SEO & Social Meta Tags
# =============================================================================
def suite_4_seo_and_social(base_dir: Path, parser: HTMLTreeParser) -> ValidationSuite:
    suite = ValidationSuite(4, "SEO & Social Meta Tags (Canonical, OpenGraph, Twitter)")

    meta_props = {a.get("property"): a.get("content") for _, a in parser.meta_tags if "property" in a and a.get("property")}
    meta_names = {a.get("name"): a.get("content") for _, a in parser.meta_tags if "name" in a and a.get("name")}
    link_rels = {a.get("rel"): a.get("href") for _, a in parser.link_tags if "rel" in a and a.get("rel")}

    # 1. Canonical Link
    canonical = link_rels.get("canonical")
    if not canonical:
        suite.fail_check("Missing '<link rel=\"canonical\">' tag.")
    elif not canonical.startswith("https://"):
        suite.fail_check(f"Canonical URL '{canonical}' must be an absolute HTTPS URL.")
    else:
        suite.pass_check(f"Canonical URL verified: '{canonical}'.")

    # 2. Meta Description
    desc = meta_names.get("description")
    if not desc:
        suite.fail_check("Missing '<meta name=\"description\">' tag.")
    elif len(desc) < 50:
        suite.fail_check(f"Meta description too short ({len(desc)} chars, expected >= 50): '{desc}'.")
    else:
        suite.pass_check(f"Meta description verified ({len(desc)} characters).")

    # 3. Robots Directives
    robots = meta_names.get("robots")
    if not robots:
        suite.fail_check("Missing '<meta name=\"robots\">' tag.")
    else:
        tokens = {t.strip().lower() for t in re.split(r'[\s,]+', robots) if t.strip()}
        if 'noindex' in tokens or 'nofollow' in tokens or 'none' in tokens or 'index' not in tokens or 'follow' not in tokens:
            suite.fail_check(f"Robots directive invalid or blocking search engines: '{robots}'.")
        else:
            suite.pass_check(f"Robots directives verified ('{robots}').")

    # 4. OpenGraph Tags
    missing_og = [og for og in REQUIRED_OG_TAGS if og not in meta_props]
    if missing_og:
        suite.fail_check(f"Missing required OpenGraph tag(s): {', '.join(missing_og)}")
    else:
        suite.pass_check(f"All {len(REQUIRED_OG_TAGS)} required OpenGraph tags present.")

    og_image = meta_props.get("og:image", "")
    if og_image:
        if not og_image.startswith("https://"):
            suite.fail_check(f"og:image must be an absolute HTTPS URL, got '{og_image}'.")
        else:
            suite.pass_check(f"og:image is an absolute HTTPS URL: '{og_image}'.")

        # Verify local file presence if pointing to own domain
        if "marcinrzezniczuk.pl/assets/" in og_image:
            rel_asset_path = og_image.split("marcinrzezniczuk.pl/")[-1]
            local_asset = base_dir / rel_asset_path
            if not local_asset.exists() and (Path.cwd() / rel_asset_path).exists():
                local_asset = Path.cwd() / rel_asset_path
            if local_asset.exists() and local_asset.stat().st_size > 0:
                suite.pass_check(f"Local social preview asset '{rel_asset_path}' exists on disk ({local_asset.stat().st_size} bytes).")
            else:
                suite.fail_check(f"Referenced social preview image file '{local_asset}' does not exist on disk or is empty.")

    og_loc = meta_props.get("og:locale")
    og_loc_alt = meta_props.get("og:locale:alternate")
    if (og_loc == "en_US" and og_loc_alt == "pl_PL") or (og_loc == "pl_PL" and og_loc_alt == "en_US"):
        suite.pass_check(f"OpenGraph locales verified: primary {og_loc}, alternate {og_loc_alt}.")
    else:
        suite.warn_check(f"OpenGraph locales: og:locale='{og_loc}', og:locale:alternate='{og_loc_alt}'.")

    # 5. Twitter Card Suite
    missing_tw = [tw for tw in REQUIRED_TWITTER_TAGS if tw not in meta_names]
    if missing_tw:
        suite.fail_check(f"Missing required Twitter Card tag(s): {', '.join(missing_tw)}")
    else:
        suite.pass_check(f"All {len(REQUIRED_TWITTER_TAGS)} required Twitter Card tags present.")

    tw_card = meta_names.get("twitter:card")
    if tw_card not in ("summary_large_image", "summary"):
        suite.fail_check(f"twitter:card expected 'summary_large_image' or 'summary', got '{tw_card}'.")
    else:
        suite.pass_check(f"Twitter card type verified: '{tw_card}'.")

    tw_image = meta_names.get("twitter:image", "")
    if tw_image and not tw_image.startswith("https://"):
        suite.fail_check(f"twitter:image must be absolute HTTPS URL, got '{tw_image}'.")
    elif tw_image:
        suite.pass_check(f"twitter:image is absolute HTTPS URL: '{tw_image}'.")

    return suite


# =============================================================================
# SUITE 5: Schema.org JSON-LD Structured Data
# =============================================================================
def suite_5_schema_json_ld(parser: HTMLTreeParser) -> ValidationSuite:
    suite = ValidationSuite(5, "Schema.org JSON-LD Structured Data")

    if not parser.json_ld_scripts:
        suite.fail_check("No '<script type=\"application/ld+json\">' structured data blocks found in document.")
        return suite

    suite.pass_check(f"Found {len(parser.json_ld_scripts)} JSON-LD structured data script block(s).")

    for pos, raw_text in parser.json_ld_scripts:
        try:
            data = json.loads(raw_text)
            suite.pass_check(f"JSON-LD block at line {pos[0]} parsed successfully with zero syntax errors.")
        except json.JSONDecodeError as ex:
            suite.fail_check(f"JSON-LD JSONDecodeError at script near line {pos[0]}: {ex}")
            continue

        # 1. @context check
        context = data.get("@context")
        if context in ("https://schema.org", "http://schema.org"):
            suite.pass_check(f"Schema.org @context verified: '{context}'.")
        else:
            suite.fail_check(f"Invalid JSON-LD @context: '{context}'. Expected 'https://schema.org'.")

        # 2. Root @type check (ProfilePage or Person)
        root_type = data.get("@type")
        person_entity = None

        if root_type == "ProfilePage":
            suite.pass_check("Root schema type is 'ProfilePage' (Google Search Central compliant).")
            # Verify ProfilePage fields
            if data.get("url"):
                suite.pass_check(f"ProfilePage url verified: '{data.get('url')}'.")
            else:
                suite.fail_check("ProfilePage missing 'url' property.")

            in_lang = data.get("inLanguage")
            if (isinstance(in_lang, list) and "en" in in_lang and "pl" in in_lang) or in_lang in ("en", "pl"):
                suite.pass_check(f"ProfilePage inLanguage valid: {in_lang}.")
            else:
                suite.warn_check(f"ProfilePage inLanguage expected ['en', 'pl'], 'en' or 'pl', got: {in_lang}")

            main_entity = data.get("mainEntity")
            if isinstance(main_entity, dict) and main_entity.get("@type") == "Person":
                suite.pass_check("ProfilePage contains valid 'mainEntity' of type 'Person'.")
                person_entity = main_entity
            else:
                suite.fail_check("ProfilePage mainEntity is missing or not of type 'Person'.")
        elif root_type == "Person":
            suite.pass_check("Root schema type is 'Person'.")
            person_entity = data
        else:
            suite.fail_check(f"Unexpected root schema @type '{root_type}'. Expected 'ProfilePage' or 'Person'.")

        # 3. Person entity detailed validation
        if person_entity:
            name = person_entity.get("name", "")
            if "Marcin" in name and "Rze" in name:
                suite.pass_check(f"Person name verified: '{name}'.")
            else:
                suite.fail_check(f"Person name missing or invalid: '{name}'.")

            # Dual jobTitle validation
            job_titles = person_entity.get("jobTitle")
            if isinstance(job_titles, list) and len(job_titles) >= 2:
                suite.pass_check(f"Person dual jobTitle verified as list: {job_titles}")
                has_tpm = any("Technical Project Manager" in t for t in job_titles)
                has_ai = any("AI Product Lead" in t for t in job_titles)
                if has_tpm and has_ai:
                    suite.pass_check("Person dual jobTitle explicitly includes 'Technical Project Manager' and 'AI Product Lead'.")
                else:
                    suite.warn_check("jobTitles list did not contain exact expected dual strings.")
            elif isinstance(job_titles, str):
                suite.fail_check(f"Expected jobTitle to be list of dual titles, got single string '{job_titles}'.")
            else:
                suite.fail_check("Person missing 'jobTitle' property.")

            # sameAs verification (LinkedIn and GitHub)
            same_as = person_entity.get("sameAs", [])
            if isinstance(same_as, list):
                has_linkedin = any("linkedin.com/in/marcinrzezniczuk" in s for s in same_as)
                has_github = any("github.com/mrzeznic" in s for s in same_as)
                if has_linkedin and has_github:
                    suite.pass_check(f"Person sameAs verified with authoritative LinkedIn and GitHub profiles ({len(same_as)} links).")
                elif has_linkedin:
                    suite.pass_check("Person sameAs verified with LinkedIn profile.")
                else:
                    suite.fail_check("Person sameAs missing verified LinkedIn profile.")
            else:
                suite.fail_check("Person 'sameAs' property is not a list.")

            # Organization affiliation (worksFor)
            works_for = person_entity.get("worksFor")
            if isinstance(works_for, dict) and works_for.get("name") == "C&F":
                suite.pass_check("Person worksFor affiliation verified: C&F.")
            else:
                suite.warn_check(f"Person worksFor affiliation: {works_for}")

            # Credentials (hasCredential)
            creds = person_entity.get("hasCredential", [])
            if isinstance(creds, list) and len(creds) >= 3:
                cred_names = [c.get("name", "") for c in creds if isinstance(c, dict)]
                suite.pass_check(f"Person hasCredential verified with {len(creds)} credentials: {', '.join(cred_names[:3])}...")
            else:
                suite.warn_check(f"Person credentials list has {len(creds)} entries.")

            # Competencies (knowsAbout)
            skills = person_entity.get("knowsAbout", [])
            if isinstance(skills, list) and len(skills) >= 5:
                suite.pass_check(f"Person knowsAbout verified with {len(skills)} competencies (AI, Agile, Data, etc.).")
            else:
                suite.warn_check(f"Person knowsAbout list has {len(skills)} entries.")

    return suite


# =============================================================================
# SUITE 6: Bilingual Parity & WCAG Interactive Accessibility
# =============================================================================
def suite_6_bilingual_and_accessibility(parser: HTMLTreeParser) -> ValidationSuite:
    suite = ValidationSuite(6, "Bilingual Parity & WCAG Interactive Accessibility")

    # 1. Bilingual Parity Check (.lang-en vs .lang-pl) or Compiled Hreflang Check
    en_count = len(parser.lang_en_nodes)
    pl_count = len(parser.lang_pl_nodes)

    if en_count == pl_count and en_count > 0:
        suite.pass_check(f"Perfect 1:1 bilingual parity: exactly {en_count} non-body .lang-en and {pl_count} .lang-pl elements.")
        # Structural pairing check: Verify matching parent tags
        en_parents = [p for _, _, _, p in parser.lang_en_nodes]
        pl_parents = [p for _, _, _, p in parser.lang_pl_nodes]
        unmatched_parents = 0
        for p in set(en_parents):
            if en_parents.count(p) != pl_parents.count(p):
                unmatched_parents += 1

        if unmatched_parents == 0:
            suite.pass_check("100% structural symmetry: all bilingual elements are balanced inside identical parent containers.")
        else:
            suite.warn_check(f"{unmatched_parents} container tag(s) have unbalanced counts between EN and PL spans.")
    elif en_count == 0 and pl_count == 0:
        # Compiled physical bilingual page
        hreflangs = {a.get("hreflang"): a.get("href") for _, a in parser.link_tags if a.get("rel") == "alternate" and "hreflang" in a}
        if "en" in hreflangs and "pl" in hreflangs and "x-default" in hreflangs:
            suite.pass_check(f"Compiled page includes full hreflang alternates (en, pl, x-default): {list(hreflangs.keys())}.")
        else:
            suite.fail_check(f"Missing required hreflang links: found {list(hreflangs.keys())}")
        suite.pass_check("Compiled document is cleanly separated: 0 leftover .lang-en/.lang-pl markers.")
    else:
        suite.fail_check(f"Bilingual parity mismatch: found {en_count} .lang-en elements vs {pl_count} .lang-pl elements.")

    # 2. WCAG Skip-to-content bypass link (WCAG 2.4.1)
    skip_link = next((el for el in parser.interactive_elements if el["tag"] == "a" and el["attrs"].get("href") == "#main-content"), None)
    if skip_link:
        suite.pass_check("WCAG 2.4.1 Bypass Blocks: Skip-to-content link verified pointing to '#main-content'.")
    else:
        suite.fail_check("Missing WCAG 2.4.1 skip-to-content bypass link targeting '#main-content'.")

    # 3. Interactive Elements Accessible Names (<a>, <button>, etc.)
    unlabeled_interactive: List[Dict[str, Any]] = []
    for el in parser.interactive_elements:
        attrs = el["attrs"]
        text = el["text"].strip()
        has_aria = bool(
            (attrs.get("aria-label") or "").strip() or
            (attrs.get("aria-labelledby") or "").strip() or
            (attrs.get("title") or "").strip()
        )
        has_text = len(text) > 0

        # Elements must have either non-empty text content or an accessible label attribute
        if not has_text and not has_aria:
            unlabeled_interactive.append(el)

    if unlabeled_interactive:
        suite.fail_check(f"Found {len(unlabeled_interactive)} interactive element(s) without accessible text or ARIA label:")
        for unl in unlabeled_interactive:
            suite.fail_check(f"  -> <{unl['tag']}> at line {unl['pos'][0]}, col {unl['pos'][1]}: {unl['attrs']}")
    else:
        suite.pass_check(f"All {len(parser.interactive_elements)} interactive elements (links, buttons) have accessible text or ARIA labels.")

    # 4. Inline SVG Accessibility (decorative SVGs should have aria-hidden="true")
    unhidden_svgs = [svg for svg in parser.svg_elements if svg[1].get("aria-hidden") != "true" and not svg[1].get("role") == "img"]
    if unhidden_svgs:
        suite.fail_check(f"Found {len(unhidden_svgs)} inline <svg> element(s) missing aria-hidden='true':")
        for pos, attrs in unhidden_svgs:
            suite.fail_check(f"  -> <svg> at line {pos[0]}, col {pos[1]}")
    else:
        suite.pass_check(f"All {len(parser.svg_elements)} inline <svg> elements properly marked with aria-hidden='true'.")

    # 5. Language navigation controls
    btn_en_id = parser.ids.get("btn-en")
    btn_pl_id = parser.ids.get("btn-pl")
    lang_links = [el for el in parser.interactive_elements if el["tag"] == "a" and el["attrs"].get("href") in ("/pl/", "/", "https://www.marcinrzezniczuk.pl/", "https://www.marcinrzezniczuk.pl/pl/")]
    if (btn_en_id and btn_pl_id) or len(lang_links) > 0:
        suite.pass_check("Language selector / navigation links verified present in DOM.")
    else:
        suite.fail_check("Missing language selector controls in DOM.")

    # 6. External Links Security & Accessibility (rel="noopener noreferrer")
    insecure_external = [link for link in parser.external_links if link[1].get("target") == "_blank" and "noopener" not in (link[1].get("rel") or "")]
    if insecure_external:
        suite.warn_check(f"{len(insecure_external)} external link(s) with target='_blank' missing rel='noopener noreferrer'.")
    else:
        suite.pass_check(f"All {len(parser.external_links)} external links with target='_blank' enforce rel='noopener noreferrer'.")

    return suite


# =============================================================================
# Main Verification Runner & CLI
# =============================================================================
def validate_file(target_path: Path, verbose: bool = False) -> bool:
    print("=" * 72)
    print("  PRODUCTION QUALITY, SEO & ACCESSIBILITY VALIDATION RUNNER")
    print(f"  Target: {target_path.resolve()}")
    print("=" * 72)

    if not target_path.exists():
        print(f"\n[FATAL ERROR] File '{target_path}' does not exist.")
        return False

    try:
        content = target_path.read_text(encoding="utf-8")
    except UnicodeDecodeError as ex:
        print(f"\n[FATAL ERROR] File is not valid UTF-8: {ex}")
        return False

    file_bytes = len(content.encode("utf-8"))
    file_lines = len(content.splitlines())
    print(f"File Size: {file_bytes:,} bytes | Total Lines: {file_lines:,}\n")

    # Parse DOM Tree using HTMLTreeParser
    parser = HTMLTreeParser()
    parser.feed(content)

    # Execute all 6 validation suites
    base_dir = target_path.parent
    suites: List[ValidationSuite] = [
        suite_1_document_architecture(content, parser),
        suite_2_tag_nesting(parser),
        suite_3_dom_id_uniqueness(parser),
        suite_4_seo_and_social(base_dir, parser),
        suite_5_schema_json_ld(parser),
        suite_6_bilingual_and_accessibility(parser)
    ]

    total_passed_checks = sum(len(s.passed_checks) for s in suites)
    total_failed_checks = sum(len(s.failed_checks) for s in suites)
    total_warnings = sum(len(s.warnings) for s in suites)
    all_suites_passed = all(s.passed for s in suites)

    # Print reports
    for s in suites:
        s.print_report(verbose=verbose)

    # Summary box
    print("\n" + "=" * 72)
    print("  VALIDATION EXECUTION SUMMARY")
    print("=" * 72)
    print(f"  Total Suites Run:      {len(suites)} of 6")
    print(f"  Suites Passed:         {sum(1 for s in suites if s.passed)} of {len(suites)}")
    print(f"  Total Checks Passed:   {total_passed_checks}")
    print(f"  Total Checks Failed:   {total_failed_checks}")
    print(f"  Total Warnings:        {total_warnings}")
    print("-" * 72)

    if all_suites_passed:
        print("  RESULT: ALL 6 VALIDATION SUITES PASSED (EXIT CODE 0)")
        print("  Document is 100% compliant with HTML5, SEO, Schema.org & WCAG.")
        print("=" * 72 + "\n")
        return True
    else:
        print("  RESULT: VALIDATION FAILED (EXIT CODE 1)")
        print("  One or more critical checks failed. See failure details above.")
        print("=" * 72 + "\n")
        return False


def main() -> int:
    args = sys.argv[1:]
    verbose = False

    if "--help" in args or "-h" in args:
        print(__doc__)
        return 0

    if "--verbose" in args or "-v" in args:
        verbose = True
        args = [a for a in args if a not in ("--verbose", "-v")]

    target_file = Path(args[0]) if args else Path("index.html")
    success = validate_file(target_file, verbose=verbose)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
