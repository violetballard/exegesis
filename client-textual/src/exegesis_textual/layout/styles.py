from __future__ import annotations

SHELL_CSS = """
    #shell-status {
        padding: 0 1;
        height: auto;
        min-height: 2;
        content-align: center middle;
    }

    #shell-command-bar {
        width: 1fr;
        height: auto;
        align-vertical: middle;
        content-align: center middle;
    }

    #shell-command-bar-top,
    #shell-command-bar-bottom,
    #shell-command-bar-file,
    #shell-command-bar-summary,
    #shell-command-bar-terminal {
        width: 1fr;
        height: 1;
        min-height: 1;
        align-vertical: middle;
        padding: 0;
        align-horizontal: center;
    }

    .command-link {
        height: 1;
        min-height: 1;
        margin-right: 1;
        padding: 0 1;
        background: transparent;
        color: $foreground;
        border: none;
        text-style: bold;
        content-align: center middle;
    }

    .command-link:hover {
        background: $secondary;
        color: $foreground;
    }

    .command-link:last-child {
        margin-right: 0;
    }

    #shell-body {
        height: 1fr;
    }

    #shell-footer-bar {
        height: auto;
        min-height: 1;
        padding: 0 1;
        align-vertical: middle;
    }

    #shell-footer-confidentiality {
        width: auto;
        min-width: 14;
        height: auto;
        min-height: 1;
        margin-right: 1;
        padding: 0 1;
        content-align: center middle;
        text-style: bold;
        border: none;
    }

    #shell-footer-hints {
        width: 1fr;
        height: auto;
        min-height: 1;
        align-vertical: middle;
        content-align: left middle;
    }

    #shell-footer-palette,
    #shell-footer-restart {
        content-align: right middle;
    }

    .footer-link {
        height: auto;
        min-height: 1;
        margin-right: 1;
        padding: 0 0;
        background: transparent;
        color: $foreground;
        border: none;
        text-style: bold;
        content-align: left middle;
    }

    .footer-link:hover {
        background: $secondary;
        color: $foreground;
    }

    #project-pane {
        width: 45;
        min-width: 45;
        border: round;
        margin-bottom: 0;
        padding: 1 1 1 1;
    }

    #project-project-actions {
        height: auto;
        margin: 0 0 1 0;
        width: 1fr;
        padding: 0;
    }

    #project-project-actions Button {
        width: 100%;
        height: 3;
        min-height: 3;
        min-width: 0;
        margin-top: 1;
        padding: 0 1;
        content-align: center middle;
    }

    #project-project-actions Button:first-child {
        margin-top: 0;
    }

    #project-header {
        width: 1fr;
        height: 3;
        min-height: 3;
        margin: 1 0 1 0;
        padding: 0 1;
        content-align: center middle;
        text-style: bold;
        border-top: hkey #00ff00;
        border-bottom: hkey #00ff00;
        border-left: none;
        border-right: none;
    }

    #project-header:focus {
        background: #00ff00;
        color: $background;
        text-style: bold;
    }

    #project-browser {
        width: 1fr;
        height: 1fr;
        padding: 0 0 1 1;
        overflow-x: hidden;
        text-wrap: wrap;
    }

    #project-actions {
        height: auto;
        padding: 0 0 1 0;
    }

    .project-action-row {
        height: 3;
        min-height: 3;
        margin-top: 1;
        align-vertical: middle;
    }

    .project-action-row Button {
        width: 100%;
        height: 3;
        min-height: 3;
        padding: 0 1;
        content-align: center middle;
    }

    #project-delete-action-row .trash-context-action {
        width: 1fr;
    }

    #project-trash-delete {
        margin-right: 1;
    }

    #document-column {
        width: 1fr;
    }

    #right-column {
        width: 45;
        min-width: 45;
    }

    #basket-pane {
        height: 15;
        min-height: 12;
        border: round;
        margin-bottom: 0;
    }

    #basket-columns {
        height: 1fr;
    }

    .basket-column {
        width: 1fr;
        margin-right: 1;
        padding: 1 1 1 1;
        border: round;
    }

    .basket-column:last-child {
        margin-right: 0;
    }

    #basket-excerpts-list,
    #basket-documents-list {
        height: 1fr;
    }

    #document-pane {
        height: 2fr;
        padding: 0;
        border: round;
        margin-top: 0;
        margin-bottom: 0;
    }

    #document-toolbar {
        height: 1;
        min-height: 1;
        padding: 0 1 0 1;
        margin-bottom: 1;
        align-vertical: middle;
    }

    #document-toolbar Button {
        height: auto;
        min-height: 1;
        min-width: 16;
        margin-right: 1;
        padding: 0 1;
        content-align: center middle;
    }

    #document-toolbar Button:last-child {
        margin-right: 0;
    }

    #document-toolbar .toolbar-spacer {
        width: 1fr;
    }

    #document-tabs {
        height: 1fr;
    }

    #document-tabs ContentTabs Underline {
        display: none;
        height: 0;
    }

    #document-tabs ContentTabs Tab {
        padding: 0 1;
        background: $surface-lighten-1;
        color: $text-muted;
    }

    #document-tabs ContentTabs Tab.-active {
        background: $surface-lighten-1;
        color: white;
        text-style: bold underline;
    }

    #document-tabs ContentTabs Tab.document-tab-trashed {
        color: #ff9f1a;
        text-style: strike;
    }

    #document-tabs ContentTabs Tab.document-tab-trashed.-active {
        color: #ff9f1a;
        text-style: bold underline strike;
    }

    #document-tabs ContentTabs Tab.document-tab-deleted {
        color: red;
        text-style: strike;
    }

    #document-tabs ContentTabs Tab.document-tab-deleted.-active {
        color: red;
        text-style: bold underline strike;
    }

    #document-tabs > ContentSwitcher {
        height: 1fr;
    }

    #document-tabs TabPane {
        padding: 0;
    }

    .document-editor {
        height: 1fr;
        line-pad: 1;
    }

    .document-preview-container {
        height: 1fr;
        display: none;
        padding: 0;
        overflow-y: auto;
    }

    .document-preview {
        height: auto;
        padding: 1 2;
    }

    #workflow-pane {
        height: 1.4fr;
        min-height: 12;
        padding: 0;
        border: round;
        margin-top: 0;
        margin-bottom: 0;
    }

    #workflow-header {
        height: 1;
        min-height: 1;
        padding: 0 1 0 0;
        align-vertical: middle;
    }

    #workflow-toolbar {
        height: 1;
        min-height: 1;
        padding: 0 1 0 0;
        align-vertical: middle;
    }

    #workflow-status {
        width: 1fr;
        height: 1;
        min-height: 1;
        margin-left: 1;
        padding: 0 1;
        background: $surface-lighten-1;
        color: $text-muted;
    }

    #workflow-toolbar .workflow-status-spacer {
        width: 16;
    }

    #workflow-header .toolbar-spacer {
        width: 1fr;
    }

    #workflow-header Button {
        height: auto;
        min-height: 1;
        min-width: 12;
        margin-left: 1;
        padding: 0 1;
        content-align: center middle;
    }

    #workflow-toolbar Button {
        height: auto;
        min-height: 1;
        min-width: 12;
        margin-left: 1;
        padding: 0 1;
        content-align: center middle;
    }

    .compact-action-primary,
    .compact-action-warning {
        height: 1;
        min-height: 1;
        padding: 0 1;
        border: none;
        text-style: bold;
        content-align: center middle;
    }

    .compact-action-primary {
        background: $primary;
        color: $text;
    }

    .compact-action-primary:hover {
        background: $secondary;
        color: $foreground;
    }

    .compact-action-warning {
        background: $warning;
        color: $text;
    }

    .compact-action-warning:hover {
        background: $warning;
        color: $text;
    }

    #workflow-composer-row {
        height: 3;
        min-height: 3;
        padding: 0 1 0 0;
        align-vertical: middle;
        margin-top: 0;
        margin-bottom: 0;
    }

    #workflow-composer-input {
        width: 1fr;
        height: 3;
        min-height: 3;
        margin-right: 1;
    }

    #workflow-send {
        height: 3;
        min-height: 3;
        width: 14;
        min-width: 14;
        margin-right: 0;
        padding: 0 1;
        content-align: center middle;
    }

    #workflow-tabs {
        height: 1fr;
        margin-right: 1;
    }

    #workflow-tabs > ContentSwitcher {
        height: 1fr;
    }

    #workflow-tabs TabPane {
        height: 1fr;
        padding: 0;
    }

    .workflow-history {
        height: 1fr;
        padding: 0 3 1 1;
        overflow-y: auto;
    }

    .workflow-history-block {
        height: auto;
        margin-top: 0;
        margin-bottom: 0;
        padding: 0 1 0 0;
    }

    .workflow-history-status {
        margin-top: 0;
        margin-bottom: 1;
    }

    .workflow-card,
    .workflow-history-placeholder {
        margin-top: 1;
    }

    .workflow-card:first-child,
    .workflow-history-placeholder:first-child {
        margin-top: 0;
    }

    .workflow-history-placeholder {
        color: $text-muted;
    }

    .workflow-history-label {
        height: 1;
        color: $primary;
        text-style: bold;
        margin: 0;
        padding: 0;
    }

    .workflow-history-message {
        height: auto;
        margin: 0;
        padding: 0 1 0 0;
    }

    .workflow-reasoning-card {
        margin-top: 1;
        margin-bottom: 1;
        padding: 0 1;
        border-left: tall $warning;
        background: $surface-lighten-1;
    }

    .workflow-reasoning-label {
        color: $warning;
    }

    .workflow-history-status-content {
        height: auto;
        min-height: 1;
        margin: 0;
        padding: 0 2 0 1;
        background: $surface-lighten-1;
        color: $text;
        border-left: thick $primary;
    }

    .workflow-history-loading-row {
        height: 1;
        min-height: 1;
        align-vertical: middle;
    }

    .workflow-history-loading {
        width: 3;
        height: 1;
        min-height: 1;
        margin-right: 1;
    }

    .workflow-history-loading-text {
        width: 1fr;
        height: 1;
        min-height: 1;
        color: $text;
    }

    .workflow-card {
        height: auto;
        min-height: 6;
        border: round;
        margin-right: 2;
        padding: 1 2 1 1;
    }

    .workflow-card-title {
        text-style: bold;
        margin-bottom: 1;
    }

    .workflow-card-meta {
        color: $text-muted;
        margin-bottom: 1;
    }

    .workflow-card-body {
        height: auto;
        margin-bottom: 1;
        padding-right: 1;
    }

    .workflow-search-result {
        margin-top: 1;
        padding: 0 2;
    }

    .workflow-search-result-row {
        height: 3;
        min-height: 3;
        align-vertical: middle;
    }

    .workflow-search-result-title {
        width: auto;
        min-width: 0;
        max-width: 1fr;
        height: 3;
        min-height: 3;
        padding: 0 1;
        margin-right: 1;
        background: #1f86dc;
        color: $text;
        border: block #1f86dc;
        text-style: none;
        content-align: left middle;
    }

    .workflow-search-result-title:hover {
        background: #1668b0;
        color: $text;
        border: block #1668b0;
    }

    .workflow-search-result-arrow {
        width: 3;
        min-width: 3;
        height: 3;
        min-height: 3;
        padding: 0;
        margin-right: 1;
        background: #1f86dc;
        color: $text;
        border: block #1f86dc;
        text-style: bold;
        content-align: center middle;
    }

    .workflow-search-result-arrow:hover {
        background: #1668b0;
        color: $text;
        border: block #1668b0;
    }

    .workflow-search-result-count {
        width: auto;
        min-width: 4;
        height: 3;
        min-height: 3;
        content-align: center middle;
        margin-right: 1;
    }

    .workflow-search-result-snippet {
        height: auto;
        min-height: 1;
        max-height: 3;
        overflow: hidden;
        padding-right: 1;
        margin-top: 1;
    }

    .workflow-history-card-actions {
        height: 1;
        min-height: 1;
    }

    .workflow-history-card-actions Button {
        height: 1;
        min-height: 1;
        min-width: 12;
        margin-right: 1;
        padding: 0 1;
        content-align: center middle;
    }

    #inspector-pane {
        height: 1fr;
        border: round;
        margin-bottom: 0;
    }

    #inspector-markdown {
        height: auto;
    }

    #inspector-markdown MarkdownBlock,
    #inspector-markdown MarkdownParagraph,
    #inspector-markdown MarkdownBullet {
        color: white;
    }

    #inspector-markdown MarkdownH1,
    #inspector-markdown MarkdownH2,
    #inspector-markdown MarkdownH3 {
        color: $primary;
    }

    #inspector-excerpt-title {
        color: $primary;
        text-style: bold;
        margin-top: 1;
    }

    #inspector-excerpt-text {
        color: white;
        margin-top: 1;
    }

    #inspector-summary-actions {
        height: auto;
        margin-top: 1;
    }

    .inspector-summary-button {
        width: 1fr;
        height: 4;
        min-height: 4;
        margin-top: 1;
        content-align: center middle;
    }

    .inspector-summary-button:first-child {
        margin-top: 0;
    }

    .shell-pane {
        padding: 1 2;
        margin: 0 1 1 1;
    }

    .modal-screen-center {
        width: 1fr;
        height: 1fr;
        align: center middle;
    }

    #transcript-warning-modal,
    #project-name-modal,
    #project-delete-confirm-modal,
    #folder-delete-confirm-modal,
    #trash-delete-confirm-modal,
    #summary-progress-modal,
    #model-settings-modal {
        width: 60;
        height: auto;
        max-width: 80%;
        padding: 2 3;
        align: center middle;
        border: round;
    }

    #model-settings-modal {
        width: 104;
        max-width: 94%;
    }

    #model-settings-status {
        min-height: 3;
        height: auto;
        margin-bottom: 1;
        padding: 1 2;
        background: $surface-lighten-1;
    }

    .model-settings-actions Button {
        min-width: 18;
    }

    #summary-progress-modal LoadingIndicator {
        height: 1;
        margin-top: 1;
        margin-bottom: 1;
    }

    #project-update-modal {
        width: 68;
        height: 28;
        max-width: 84%;
        padding: 2 3;
        align: center middle;
        border: round;
    }

    #project-picker-modal {
        width: 72;
        height: 28;
        max-width: 88%;
        padding: 2 3;
        align: center middle;
        border: round;
    }

    #trash-document-modal {
        width: 76;
        height: auto;
        max-width: 90%;
        padding: 2 3;
        align: center middle;
        border: round;
    }

    #projects-directory-modal {
        width: 84;
        height: 30;
        max-width: 92%;
        padding: 2 3;
        align: center middle;
        border: round;
    }

    #duplicate-document-modal {
        width: 96;
        height: auto;
        max-width: 96%;
        padding: 2 2;
        align: center middle;
        border: round;
    }

    #duplicate-project-modal {
        width: 84;
        height: auto;
        max-width: 94%;
        padding: 2 3;
        align: center middle;
        border: round;
    }

    #import-browser-modal {
        width: 98;
        height: 34;
        max-width: 96%;
        padding: 2 2;
        align: center middle;
        border: round;
    }

    #import-browser-path {
        margin-bottom: 1;
        color: $text-muted;
    }

    #projects-directory-path {
        margin-bottom: 1;
        color: $text-muted;
    }

    #projects-directory-create-row {
        height: 3;
        margin-bottom: 1;
    }

    #projects-directory-new-folder-input {
        width: 1fr;
        margin-right: 1;
    }

    #projects-directory-create-folder {
        width: 20;
    }

    #projects-directory-options {
        height: 1fr;
        margin-bottom: 1;
    }

    #import-browser-search {
        margin-bottom: 1;
    }

    #import-browser-help {
        color: $text-muted;
        margin-bottom: 1;
    }

    #import-browser-options {
        height: 1fr;
        margin-bottom: 1;
    }

    #import-progress-modal {
        width: 72;
        height: auto;
        max-width: 90%;
        padding: 2 3;
        align: center middle;
        border: round;
    }

    #import-progress-current,
    #import-progress-counts {
        margin-bottom: 1;
    }

    #import-progress-status {
        color: $text-muted;
        margin-bottom: 1;
    }

    .import-progress-actions {
        align: center middle;
    }

    #transcript-warning-text {
        margin-bottom: 1;
    }

    #project-delete-confirm-text {
        margin-bottom: 2;
    }

    #trash-document-details {
        margin-bottom: 2;
    }

    #project-modal-title {
        margin-bottom: 1;
    }

    #project-update-modal-subtitle {
        margin-bottom: 1;
    }

    #project-name-input,
    #project-rename-active-input,
    #project-rename-input,
    #project-picker-options {
        margin-bottom: 1;
    }

    #project-update-title-input,
    #project-update-folder-tree,
    #project-update-selected-folder {
        margin-bottom: 1;
    }

    #project-update-folder-tree {
        height: 1fr;
        border: tall $panel;
        padding: 0 1;
    }

    #project-update-selected-folder {
        color: $text-muted;
    }

    #project-picker-options {
        height: 1fr;
    }

    .project-modal-actions {
        height: auto;
        margin-top: 1;
        width: 100%;
        align: center middle;
    }

    .project-modal-actions Button {
        height: 3;
        min-height: 3;
        padding: 0 1;
        margin-right: 1;
        content-align: center middle;
    }

    #project-name-cancel,
    #project-rename-active-cancel,
    #project-picker-cancel,
    #projects-directory-cancel,
    #project-rename-cancel,
    #project-folder-cancel,
    #project-update-cancel,
    #project-duplicate-cancel,
    #duplicate-cancel-import,
    #import-browser-cancel {
        height: 3;
        min-height: 3;
        padding: 0 1;
        content-align: center middle;
        background: $surface;
        color: $text;
        border-top: tall $surface-lighten-2;
        border-bottom: tall $surface-lighten-1;
    }

    #project-name-cancel:hover,
    #project-rename-active-cancel:hover,
    #project-picker-cancel:hover,
    #projects-directory-cancel:hover,
    #project-rename-cancel:hover,
    #project-folder-cancel:hover,
    #project-update-cancel:hover,
    #project-duplicate-cancel:hover,
    #duplicate-cancel-import:hover,
    #import-browser-cancel:hover {
        background: $surface-lighten-1;
        color: $text;
        border-top: tall $surface-lighten-3;
    }

    .import-browser-actions {
        align: center middle;
    }

    .import-browser-actions Button {
        margin-right: 1;
    }

    #import-browser-import-selected {
        width: 14;
    }

    #import-browser-cancel {
        width: 14;
    }

    #import-browser-import-files-from-folder {
        width: 16;
    }

    #import-browser-import-folder {
        width: 22;
    }

    .confirm-modal-button {
        height: 3;
        min-height: 3;
        width: 22;
        padding: 0 1;
        text-style: bold;
        content-align: center middle;
    }

    .trash-modal-actions {
        width: 100%;
        align: center middle;
    }

    .trash-modal-side-button {
        width: 12;
    }

    .trash-modal-danger-button {
        width: 26;
    }

    .trash-modal-button {
        height: 3;
        min-height: 3;
        padding: 0 1;
        text-style: bold;
        content-align: center middle;
    }

    .trash-modal-button.-primary:hover {
        background: $secondary;
        color: $foreground;
    }

    .trash-modal-button.-warning:hover {
        background: #d88818;
        color: $text;
    }

    .trash-modal-button.-error:hover {
        background: #d93636;
        color: $text;
    }

    .duplicate-modal-actions {
        margin-top: 1;
        align: center middle;
    }

    .duplicate-modal-actions Button {
        width: 17;
        margin-right: 1;
    }

    .duplicate-modal-cancel-actions {
        margin-top: 1;
        align: center middle;
    }

    .duplicate-modal-cancel-actions Button {
        width: 18;
    }

    #duplicate-replace-all,
    #duplicate-cancel {
        width: 18;
    }
    """
