package cmd

import (
	"github.com/spf13/cobra"
	"os"
)

var (
	releaseVersion string
	eventName      string
	eventState     string
)

var rootCmd = &cobra.Command{
	Use:   "db",
	Short: "A CLI tool for gp release engineering",
	Long: `A CLI tool for gp release engineering
Using this tool to do sql query in database`,
}

func Execute() {
	if err := rootCmd.Execute(); err != nil {
		os.Exit(1)
	}
}
