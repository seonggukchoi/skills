---
name: doc-to-markdown
description: >-
  Use when the user requests converting a document file to markdown — e.g.,
  "convert PDF", "convert document", "convert to markdown", "convert docx",
  "convert Hangul (HWP)", "doc to md", "PDF to markdown", "hwp conversion" — or
  when the contents of a document file need to be turned into markdown during a
  conversation. Whenever the user shows intent to extract text from or convert
  the format of a document file — e.g., "turn this document into markdown",
  "clean up the contents of this PDF", "read this HWP file into markdown",
  "put this Excel data into a markdown table", "convert this file", "extract
  the text from this document" — use this skill even if 'markdown' is not
  explicitly mentioned.
context: fork
agent: doc-to-markdown
argument-hint: "[document file path] [output path (optional)]"
---

Convert the document file given in $ARGUMENTS to markdown.

---

## Reading Strategy: Skills First

### Priority 1: Delegate to a Dedicated Skill

For the following extensions, you **must** use the corresponding skill to extract the content. Follow the skill's workflow and tools exactly.

| Extension       | Delegate to skill | Notes                       |
| --------------- | ----------------- | --------------------------- |
| `.pdf`          | `pdf`             |                             |
| `.docx`         | `docx`            |                             |
| `.doc`          | `docx`            | Attempt with the docx skill |
| `.pptx`         | `pptx`            |                             |
| `.xlsx`, `.csv` | `xlsx`            |                             |
| `.hwp`, `.hwpx` | `hwp`             |                             |

### Priority 2: Convert with External Tools

For formats without a dedicated skill, use external tools:

| Extension | Conversion tool          | Example command                                      |
| --------- | ------------------------ | --------------------------------------------------- |
| `.rtf`    | `pandoc`                 | `pandoc -f rtf -t markdown -o output.md input.rtf`   |
| `.odt`    | `pandoc`                 | `pandoc -f odt -t markdown -o output.md input.odt`   |
| `.epub`   | `pandoc`                 | `pandoc -f epub -t markdown -o output.md input.epub` |
| `.pages`  | `libreoffice` → `pandoc` | Convert via libreoffice                              |

Even for document formats not in the list above, attempt conversion if the format allows text extraction.

### Priority 3: Read Directly with the Read Tool

Read image-based documents (scanned documents such as .png, .jpg) directly with the Read tool.

### When an External Tool Is Missing

1. First check whether the tool exists with `which pandoc`, `which libreoffice`, etc.
2. If the tool is missing, **do not install it**. Tell the user the required tool and its install command, then stop.

---

## Conversion Procedure

### 1. Verify Input

Verify the file path and extension. If the file doesn't exist, point out the path and stop.

### 2. Determine the Output Path

If no output path is specified, use the same directory as the original with a `.md` extension (e.g., `report.pdf` → `report.md`). If a markdown file with the same name already exists, ask the user whether to overwrite it.

### 3. Extract the Content

Depending on the extension, choose the appropriate method — a dedicated skill, an external tool, or the Read tool — and extract the content.

### 4. Analyze Structure and Refine the Markdown

Identify the logical structure of the extracted content (heading hierarchy, body text, tables, lists, images, formulas, etc.) and generate the final markdown according to the conversion rules below. The output of external tools or skills may contain unnecessary tags, broken formatting, or excessive line breaks, so put it through a refinement pass.

### 5. Save the File and Return the Result

Save with the Write tool and report the conversion result per the "Result Return Format" section.

---

## Error Handling

### When a Skill or External Tool Fails

1. Check the error message to determine the cause (encoding issues, unsupported format, etc.).
2. If an alternative tool exists, try it (e.g., if pandoc fails, convert via libreoffice).
3. If the fallback also fails, try reading directly with the Read tool — Read can handle PDF and image formats.
4. If every method fails, report the methods tried and the errors to the user, then stop.

### Encrypted or Protected Files

Password-protected documents cannot be processed. Tell the user to remove the password and try again.

### Very Large Files

Large documents of several hundred pages or more may cause memory problems. If an error occurs, explain how to process it by splitting it into page ranges.

---

## Conversion Rules

### Basic Rules

The core rules that apply to all document types.

#### Heading Hierarchy

- Document title → `# Title`
- Chapter → `## Chapter Title`
- Section → `### Section Title`
- Subsection → `#### Subsection Title`
- For five levels or deeper, use at most `#####`. Anything beyond that, render as **bold text**.

#### Text Formatting

| Source formatting | Markdown conversion |
| ----------------- | ------------------- |
| Bold              | `**text**`          |
| Italic            | `*text*`            |
| Underline         | `<u>text</u>`       |
| Strikethrough     | `~~text~~`          |
| Inline code       | `` `code` ``        |

#### Tables

- Use markdown table syntax (`| Header | Header |`).
- Include a header row and a separator line (`|---|---|`).
- Render line breaks within a cell as `<br>`.
- Render complex tables with merged cells as HTML `<table>`.

#### Lists

- Ordered list → `1. Item`
- Unordered list → `- Item`
- Express nesting with 4-space indentation.

#### Code

- Code block → triple backticks + language identifier
- Inline code → single backticks

#### Images/Figures

- Describe the image content in text: `> [Figure: description text]`
- For charts/graphs, reproduce the data as a markdown table where possible.

#### Formulas

- Inline formula → `$formula$`
- Block formula → `$$formula$$`
- Use LaTeX syntax.

#### Footnotes/References

- Footnote → `[^1]`, with `[^1]: footnote content` at the end of the document
- Hyperlink → `[text](URL)`
- Organize the bibliography into a `## References` section at the end of the document.

### Special Elements

- Quote → `> quote`
- Callout/note boxes → `> [!NOTE]`, `> [!WARNING]`, `> [!TIP]` (GFM syntax)

### What to Remove

| Element | Reason for removal |
| --- | --- |
| Headers/footers (page numbers, repeated titles) | Markdown has no concept of pages |
| Table of contents (TOC) | Markdown tools can auto-generate it from headings |
| Watermarks | Meta information, not content |
| Blank pages/blank slides | They have no content |
| Page/slide breaks | Markdown separates sections with headings |

---

## Output Quality Standards

### Completeness Principle (Top Priority)

The goal of conversion is to move the original document's content into markdown without loss:

- Convert **every single sentence** of the original document.
- Do not summarize, abridge, paraphrase, or omit sentences — this is a format conversion, not editing.
- Convert paragraphs as-is, however long they are.
- Include repetitive or seemingly unimportant content as long as it's in the original.
- If the converted text's length differs markedly from the original, there's an omission, so recheck.

### Formatting and Consistency

- Preserve the **meaning and structure** of the original document as much as possible.
- Clean up unnecessary whitespace, broken characters, and duplicate line breaks.
- Check the consistency of the markdown syntax (unclosed tags, broken tables, etc.).
- Accurately preserve hanja annotations and special characters in Korean documents.
- Keep a single blank line between paragraphs to ensure readability.

---

## Result Return Format

After conversion, return the following information:

1. **Save path**: the absolute path of the generated markdown file
2. **Conversion summary**: source format, total page/slide/sheet count (estimated), number of main sections, and counts of tables/images/formulas
3. **Loss list**: elements lost or approximated during conversion (write "None" if there are none)
4. **Tools used**: the skill or external tool used for the conversion
