package cmd

import (
	"database/sql"
	"fmt"

	"log"
	"sync"

	_ "github.com/lib/pq"
	"github.com/spf13/cobra"
)

type DBInfo struct {
	host string
	port int
	user string
	//password string
	dbname string
}

func NewDBInfo(host string, port int, user string, dbname string) *DBInfo {
	return &DBInfo{
		host:   host,
		port:   port,
		user:   user,
		dbname: dbname,
	}
}

func (d *DBInfo) CreateDB() (*sql.DB, error) {
	psqlInfo := fmt.Sprintf("host=%s port=%d user=%s "+
		"dbname=%s sslmode=disable",
		d.host, d.port, d.user, d.dbname)

	db, err := sql.Open("postgres", psqlInfo)
	if err != nil {
		return nil, err
	}

	err = db.Ping()
	if err != nil {
		return nil, err
	}
	return db, nil
}

func QueryDB(db *sql.DB, releaseVersion string, eventName string, eventState string) {
	sqlStatement := `
INSERT INTO
   orig_release_train_event
values
   (
      $1, $2, current_timestamp, $3
   )
RETURNING *
`
	var version, event, time, state string
	err := db.QueryRow(sqlStatement, releaseVersion, eventName, eventState).Scan(&version, &event, &time, &state)
	if err != nil {
		panic(err)
	}
	fmt.Println("New record is:", version, event, time, state)
}

var (
	insertCmdFlagsInit sync.Once
)

var insertCmd = &cobra.Command{
	Use:   "insert <-v release_version> <-e event_name> <-s event_state>",
	Short: "insert a query to database",
	Run: func(cmd *cobra.Command, args []string) {
		dbInfo := NewDBInfo("localhost", 5432, "nwu", "nwu")
		db, err := dbInfo.CreateDB()
		if err != nil {
			panic(err)
		}

		defer db.Close()
		fmt.Println("Successfully connect to database!")

		QueryDB(db, releaseVersion, eventName, eventState)
	},
}

func init() {
	insertCmdFlagsInit.Do(func() {
		insertCmd.Flags().StringVarP(&releaseVersion, "version", "v", "", "release version")
		insertCmd.Flags().StringVarP(&eventName, "name", "e", "", "event name")
		insertCmd.Flags().StringVarP(&eventState, "state", "s", "", "event state")
	})

	insertCmdRequiredFlags := []string{
		"version",
		"name",
		"state",
	}

	for _, flag := range insertCmdRequiredFlags {
		err := insertCmd.MarkFlagRequired(flag)
		if err != nil {
			log.Fatal(err)
		}
	}

	rootCmd.AddCommand(insertCmd)
}
