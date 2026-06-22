---
name: go-tui
description: >-
  Patterns for building Go CLI tools using Cobra, Bubble Tea TUI apps, lipgloss
  styling, cmd/internal project structure, or bubbletea/bubbles imports.
---

# Go CLI/TUI Development Patterns

**Version:** 1.0.0
**Auto-activates when:** Working on Go CLI tools using Cobra, Bubble Tea TUI apps, lipgloss styling, projects with cmd/internal structure, or bubbletea/bubbles imports.

---

## 🎯 Purpose

Patterns for building Go CLI tools with optional TUI. Stack: **cobra + bubbletea + lipgloss + bubbles**.

Use this skill when:
- Scaffolding a new Go CLI/TUI project
- Adding a TUI to an existing Go tool
- Reviewing or refactoring Go TUI code
- Debugging Bubble Tea model/update/view issues

---

## 🏗️ Project Structure

```
my-tool/
├── cmd/my-tool/
│   └── main.go              # Entry point (<15 lines)
├── internal/
│   ├── cli/
│   │   └── root.go          # Cobra root command + mode dispatch
│   └── tui/
│       ├── app.go           # Model, Init, Update, View, Run
│       ├── styles.go        # All lipgloss styles (separate file)
│       └── commands.go      # Async tea.Cmd functions (when app.go grows)
├── Makefile
└── go.mod
```

**Conventions:**
- Binary name = directory name under `cmd/`
- Split `app.go` into `app.go` + `commands.go` + `styles.go` once it grows
- Business logic lives in `internal/<domain>/`, not in `internal/tui/`

---

## 📦 Dependencies

```bash
go mod init github.com/sebastianlinares/my-tool
go get github.com/spf13/cobra@latest
go get github.com/charmbracelet/bubbletea@latest
go get github.com/charmbracelet/lipgloss@latest
go get github.com/charmbracelet/bubbles@latest   # spinner, viewport, textarea
```

---

## 🔧 Core Patterns

### Entry Point — `cmd/my-tool/main.go`

Keep it under 15 lines. Delegates entirely to `cli.Execute()`.

```go
package main

import (
    "fmt"
    "os"

    "github.com/sebastianlinares/my-tool/internal/cli"
)

func main() {
    if err := cli.Execute(); err != nil {
        fmt.Fprintf(os.Stderr, "Error: %v\n", err)
        os.Exit(1)
    }
}
```

---

### Mode Dispatch — `internal/cli/root.go`

Three modes: pipe → stdout, flag → flag mode, default → TUI.

```go
package cli

import (
    "os"

    "github.com/spf13/cobra"
    "github.com/sebastianlinares/my-tool/internal/tui"
)

var rootCmd = &cobra.Command{
    Use:   "my-tool",
    Short: "Tool description",
    RunE:  run,
}

func Execute() error {
    return rootCmd.Execute()
}

func init() {
    // rootCmd.Flags().StringVar(&myFlag, "flag-name", "", "Description")
}

func run(cmd *cobra.Command, args []string) error {
    // Pipe detection: skip TUI when stdout is piped
    stat, _ := os.Stdout.Stat()
    if (stat.Mode() & os.ModeCharDevice) == 0 {
        return runStdout()
    }
    return tui.Run()
}

func runStdout() error {
    // Print result to stdout (no TUI)
    return nil
}
```

---

### Bubble Tea Model — `internal/tui/app.go`

Full pattern with `tea.WindowSizeMsg`, state-scoped key handling, and help bar.

```go
package tui

import (
    "github.com/charmbracelet/bubbles/spinner"
    tea "github.com/charmbracelet/bubbletea"
)

type state int

const (
    stateLoading state = iota
    stateReady
)

type resultMsg struct {
    data string
    err  error
}

type model struct {
    state   state
    spinner spinner.Model
    result  string
    err     error
    width   int
    height  int
}

func InitialModel() model {
    s := spinner.New()
    s.Spinner = spinner.Dot
    s.Style = spinnerStyle
    return model{state: stateLoading, spinner: s}
}

func (m model) Init() tea.Cmd {
    return tea.Batch(m.spinner.Tick, doWork())
}

func (m model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
    // 1. Window resize — always handle first
    if msg, ok := msg.(tea.WindowSizeMsg); ok {
        m.width = msg.Width
        m.height = msg.Height
        return m, nil
    }

    // 2. Custom messages
    switch msg := msg.(type) {
    case resultMsg:
        if msg.err != nil {
            m.err = msg.err
            return m, tea.Quit
        }
        m.state = stateReady
        m.result = msg.data
        return m, nil
    }

    // 3. Key messages — scoped to current state
    if msg, ok := msg.(tea.KeyMsg); ok {
        switch m.state {
        case stateLoading:
            if msg.String() == "ctrl+c" {
                return m, tea.Quit
            }

        case stateReady:
            switch msg.String() {
            case "q", "ctrl+c":
                return m, tea.Quit
            }
        }
    }

    // 4. Sub-component updates
    if m.state == stateLoading {
        var cmd tea.Cmd
        m.spinner, cmd = m.spinner.Update(msg)
        return m, cmd
    }

    return m, nil
}

func (m model) View() string {
    if m.err != nil {
        return errorStyle.Render("Error: "+m.err.Error()) + "\n"
    }
    switch m.state {
    case stateLoading:
        return "\n" + m.spinner.View() + " Working...\n"
    case stateReady:
        help := helpStyle.Render("q quit")
        return titleStyle.Render("Result") + "\n" + m.result + "\n" + help
    }
    return ""
}

func Run() error {
    p := tea.NewProgram(InitialModel(), tea.WithAltScreen())
    _, err := p.Run()
    return err
}
```

---

### Async Work Pattern

```go
// 1. Define result message type
type resultMsg struct {
    data string
    err  error
}

// 2. Command function — runs in goroutine, never blocks Update
func doWork() tea.Cmd {
    return func() tea.Msg {
        data, err := someSlowOperation()
        return resultMsg{data: data, err: err}
    }
}

// 3. Launch in Init (or on user action in Update)
func (m model) Init() tea.Cmd {
    return tea.Batch(m.spinner.Tick, doWork())
}

// 4. Handle in Update
case resultMsg:
    m.state = stateReady
    m.result = msg.data
    return m, nil
```

✅ Return `tea.Cmd` for all I/O — the runtime runs it in a goroutine
❌ Never call blocking operations directly inside `Update()`

---

### Styles — `internal/tui/styles.go`

Always separate from `app.go`. Reference: [aicommit-go/internal/tui/styles.go](../aicommit-go/internal/tui/styles.go)

```go
package tui

import "github.com/charmbracelet/lipgloss"

var (
    // Colors
    primaryColor = lipgloss.Color("#7C3AED")
    successColor = lipgloss.Color("#10B981")
    errorColor   = lipgloss.Color("#EF4444")
    mutedColor   = lipgloss.Color("#6B7280")
    borderColor  = lipgloss.Color("#374151")

    titleStyle = lipgloss.NewStyle().
            Bold(true).
            Foreground(primaryColor).
            MarginBottom(1)

    spinnerStyle = lipgloss.NewStyle().
            Foreground(primaryColor)

    helpStyle = lipgloss.NewStyle().
            Foreground(mutedColor).
            MarginTop(1)

    errorStyle = lipgloss.NewStyle().
            Foreground(errorColor).
            Bold(true)

    successStyle = lipgloss.NewStyle().
            Foreground(successColor).
            Bold(true)

    keyStyle = lipgloss.NewStyle().
            Foreground(primaryColor).
            Bold(true)

    viewportStyle = lipgloss.NewStyle().
            BorderStyle(lipgloss.RoundedBorder()).
            BorderForeground(borderColor).
            Padding(1, 2)
)
```

---

## 🎹 Key Bindings

**Conventions:**
- `j`/`k` or `↑`/`↓` — move cursor
- `Enter` — select/confirm
- `Esc` — back/cancel
- `q` / `Ctrl+C` — quit

**Help bar pattern** (per state in `View()`):
```go
help := fmt.Sprintf(
    "%s copy  %s edit  %s quit",
    keyStyle.Render("c"),
    keyStyle.Render("e"),
    keyStyle.Render("q"),
)
return titleStyle.Render("Title") + "\n" + content + "\n" + helpStyle.Render(help)
```

---

## 🔨 Makefile

```makefile
.PHONY: build install run clean

build:
	go build -o bin/my-tool ./cmd/my-tool

install:
	go install ./cmd/my-tool

run:
	go run ./cmd/my-tool

clean:
	rm -rf bin/
```

---

## ⚠️ Anti-Patterns

❌ **No `tea.WithAltScreen()`** — TUI renders inline, leaves artifacts on exit

❌ **Blocking in `Update()`** — freezes the event loop; wrap all I/O in `tea.Cmd`

❌ **Ignoring `tea.WindowSizeMsg`** — viewport/textarea will break on terminal resize; always handle it

❌ **Business logic in `internal/tui/`** — keep domain logic in `internal/<domain>/`, tui only renders

❌ **Inline styles in `View()`** — extract all lipgloss styles to `styles.go`

❌ **Flat key handling** — use state-scoped switch (`switch m.state { case ...: switch msg.String() }`) not one flat switch

❌ **Giant `app.go`** — split into `app.go` (model/init/update/view) + `commands.go` (async cmds) + `styles.go`

---

## ✅ Review Checklist

When scaffolding or reviewing a Go TUI project:

- [ ] `main.go` is under 15 lines
- [ ] Pipe detection in `root.go`
- [ ] `tea.WithAltScreen()` used in `Run()`
- [ ] `tea.WindowSizeMsg` handled in `Update()`
- [ ] All async work uses `tea.Cmd` (nothing blocks `Update`)
- [ ] Styles in separate `styles.go`
- [ ] State enum with `iota`
- [ ] Error state rendered in `View()`
- [ ] Help bar shows current-state keys
- [ ] Makefile has `build` / `install` / `run` / `clean`

---

**Last Updated:** 2026-02-18
**Skill Version:** 1.0.0
