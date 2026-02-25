# TODO: Feature Parity with google-docs-mcp

This file tracks features from [@a-bonus/google-docs-mcp](https://github.com/a-bonus/google-docs-mcp) that we may want to implement in our custom server.

## Current Status

**What we have (18 tools):**
- ✅ Basic document CRUD (create, read, update)
- ✅ Text operations (insert, append, replace, delete ranges)
- ✅ Basic formatting (bold, italic, underline, font size/family)
- ✅ Spreadsheet read/write (ranges, values)
- ✅ File listing and search
- ✅ Batch updates (advanced custom API requests)

## Priority 1: Essential Document Editing Features

### Comments System
- [ ] List comments from a document with metadata
- [ ] Get specific comment details
- [ ] Create anchored comments at specific text positions
- [ ] Reply to existing comments
- [ ] Resolve comments
- [ ] Delete comments

**Value:** Critical for collaborative editing workflows

**API Reference:**
- [Comments.list](https://developers.google.com/docs/api/reference/rest/v1/documents.comments/list)
- [Comments.create](https://developers.google.com/docs/api/reference/rest/v1/documents.comments/create)
- [Comments.get](https://developers.google.com/docs/api/reference/rest/v1/documents.comments/get)

### Image Insertion
- [ ] Insert images from URLs
- [ ] Insert images from local files (upload to Drive first)
- [ ] Set image size and positioning
- [ ] Inline images vs positioned images

**Value:** High - documents often need visual content

**API Reference:**
- [InsertInlineImageRequest](https://developers.google.com/docs/api/reference/rest/v1/documents/request#insertinlineimagerequest)

### Tables
- [ ] Insert tables with specified rows/columns
- [ ] Add/delete table rows
- [ ] Add/delete table columns
- [ ] Update table cell content
- [ ] Format table cells
- [ ] Merge/split cells

**Value:** High - essential for structured data in documents

**API Reference:**
- [InsertTableRequest](https://developers.google.com/docs/api/reference/rest/v1/documents/request#inserttablerequest)
- [InsertTableRowRequest](https://developers.google.com/docs/api/reference/rest/v1/documents/request#inserttablerowrequest)

### Advanced Text Formatting
- [ ] Text colors (foreground/background)
- [ ] Links/hyperlinks
- [ ] Paragraph alignment (left, center, right, justify)
- [ ] Line spacing
- [ ] Paragraph spacing (before/after)
- [ ] Indentation (first line, hanging)
- [ ] Strikethrough
- [ ] Subscript/superscript

**Value:** High - professional documents need rich formatting

**API Reference:**
- [TextStyle](https://developers.google.com/docs/api/reference/rest/v1/documents#textstyle)
- [ParagraphStyle](https://developers.google.com/docs/api/reference/rest/v1/documents#paragraphstyle)

### Page Breaks
- [ ] Insert page breaks at specific locations

**Value:** Medium - useful for document structure

**API Reference:**
- [InsertPageBreakRequest](https://developers.google.com/docs/api/reference/rest/v1/documents/request#insertpagebreakrequest)

## Priority 2: File Management

### Drive Operations
- [ ] Move files between folders
- [ ] Copy files
- [ ] Rename files
- [ ] Delete files (trash)
- [ ] Permanently delete files
- [ ] Create folders
- [ ] List folder contents
- [ ] Share files (permissions)

**Value:** High - essential for file organization

**API Reference:**
- [Files.update](https://developers.google.com/drive/api/reference/rest/v3/files/update)
- [Files.copy](https://developers.google.com/drive/api/reference/rest/v3/files/copy)
- [Files.delete](https://developers.google.com/drive/api/reference/rest/v3/files/delete)

### Template Support
- [ ] Create documents from templates
- [ ] Copy template structure
- [ ] Variable substitution in templates

**Value:** Medium - useful for repetitive documents

## Priority 3: Advanced Features

### Markdown Support
- [ ] Convert Google Docs to Markdown
- [ ] Convert Markdown to Google Docs
- [ ] Round-trip conversion preserving formatting
- [ ] Handle nested lists, tables, code blocks

**Value:** High for developers - enables local editing

**Implementation Notes:**
- Need custom parser for Docs → Markdown
- Use batch updates for Markdown → Docs
- Reference: HTML/Markdown converters like pandoc

### Multi-tab Documents
- [ ] Create documents with multiple tabs
- [ ] Navigate between tabs
- [ ] Get content from specific tabs
- [ ] Edit content in specific tabs

**Value:** Medium - useful for complex documents

**API Reference:**
- [Tabs](https://developers.google.com/docs/api/reference/rest/v1/documents#Tab)

### Sheets Advanced Formatting
- [ ] Cell text formatting (bold, colors, fonts)
- [ ] Cell background colors
- [ ] Cell borders
- [ ] Cell alignment
- [ ] Number formatting
- [ ] Freeze rows/columns
- [ ] Data validation (dropdowns)
- [ ] Conditional formatting
- [ ] Protected ranges

**Value:** High - professional spreadsheets need formatting

**API Reference:**
- [Spreadsheets.batchUpdate](https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets/batchUpdate)
- [CellFormat](https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets/cells#CellFormat)

### Enhanced Search
- [ ] Full-text search across all documents
- [ ] Filter by date ranges
- [ ] Filter by owner
- [ ] Filter by sharing status
- [ ] Filter by starred status
- [ ] Search within specific folders

**Value:** Medium - useful for large document libraries

## Implementation Strategy

### Phase 1: Core Editing (Priority 1)
1. Start with comments system (most requested)
2. Add tables (essential for many documents)
3. Add advanced text formatting (colors, links, alignment)
4. Add image insertion
5. Add page breaks

### Phase 2: File Management (Priority 2)
1. Implement basic file operations (move, copy, rename, delete)
2. Add folder management
3. Add template support

### Phase 3: Advanced Features (Priority 3)
1. Markdown conversion (high value for developers)
2. Sheets formatting
3. Multi-tab documents
4. Enhanced search

## Reference Implementation

The [@a-bonus/google-docs-mcp](https://github.com/a-bonus/google-docs-mcp) server has all these features implemented. We can:

1. **Study their implementation** for API patterns
2. **Test their server** to understand UX
3. **Keep both servers** - use theirs for features we haven't implemented
4. **Gradually migrate** as we add features to our server

## Why Build Our Own?

Even with the excellent @a-bonus server, our custom server provides:

1. **Box credential integration** - seamless multi-machine setup
2. **Python implementation** - easier to extend with our existing Python tools
3. **Learning** - deep understanding of Google APIs
4. **Customization** - add features specific to our workflows
5. **Control** - no dependency on third-party npm packages

## Next Steps

When ready to implement a feature:

1. Review the Google API documentation (linked above)
2. Check @a-bonus implementation for reference
3. Add method to `docs_client.py`
4. Add tool definition to `server.py`
5. Test thoroughly with `test_server.py`
6. Update README with new capability
7. Commit and push

---

**Last Updated:** 2026-02-25
