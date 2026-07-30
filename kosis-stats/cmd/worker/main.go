package main

import (
	"errors"
	"kosis/internal/config"
	"kosis/internal/db"
	"kosis/internal/tasks"
	"log"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/hibiken/asynq"
)

func main() {
	cfg, err := config.LoadConfig()
	if err != nil {
		log.Fatalf("Failed to load configuration: %v", err)
	}

	db, err := db.InitDB(cfg.DatabaseURL)
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}
	log.Println("Worker connected to database.")

	redisOpt, err := asynq.ParseRedisURI(cfg.RedisURL)
	if err != nil {
		log.Fatalf("Failed to parse Redis URL: %v", err)
	}

	asynqClient := asynq.NewClient(redisOpt)
	defer asynqClient.Close()

	inspector := asynq.NewInspector(redisOpt)
	defer func() {
		if err := inspector.Close(); err != nil {
			log.Printf("Failed to close inspector: %v", err)
		}
	}()

	scheduler := asynq.NewScheduler(redisOpt, &asynq.SchedulerOpts{})
	fetchReportsTask, err := tasks.NewFetchReportsTask(nil, nil)
	if err != nil {
		log.Fatalf("Failed to create fetch reports task: %v", err)
	}

	fetchCompaniesTask, err := tasks.NewFetchCompaniesTask()
	if err != nil {
		log.Fatalf("Failed to create fetch companies task: %v", err)
	}

	// every hour at midnight
	entryID, err := scheduler.Register("0 0 * * *", fetchCompaniesTask, asynq.Queue("default"))
	if err != nil {
		log.Fatalf("Failed to register periodic task: %v", err)
	}
	log.Printf("Registered periodic task: %s (EntryID: %s)", fetchCompaniesTask.Type(), entryID)

	// every hour
	// entryID, err = scheduler.Register("0 * * * *", fetchReportsTask, asynq.Queue("default"))
	// if err != nil {
	// 	log.Fatalf("Failed to register periodic task: %v", err)
	// }
	// log.Printf("Registered periodic task: %s (EntryID: %s)", fetchReportsTask.Type(), entryID)

	srv := asynq.NewServer(
		redisOpt,
		asynq.Config{
			// Specify different queues or priorities if needed
			Queues: map[string]int{
				"default": 1,
			},
			Concurrency: 1, // Max 10 concurrent jobs
		},
	)

	taskProcessor := tasks.NewTaskProcessor(db, cfg)

	mux := asynq.NewServeMux()
	mux.HandleFunc(
		tasks.TypeTaskFetchReports,
		taskProcessor.HandleFetchReportsTask,
	)

	mux.HandleFunc(
		tasks.TypeTaskFetchCompanies,
		taskProcessor.HandleFetchCompaniesTask,
	)

	// To submit manually
	// asynqClient.Enqueue(fetchCompaniesTask)

	// To submit manually
	deleted, err := deleteTasksByType(inspector, "default", tasks.TypeTaskFetchReports)
	if err != nil {
		if !errors.Is(err, asynq.ErrQueueNotFound) {
			log.Fatalf("Failed to clean fetch reports tasks: %v", err)
		}
	}

	if deleted > 0 {
		log.Printf("Deleted %d existing fetch reports tasks", deleted)
	}

	if _, err := asynqClient.Enqueue(fetchReportsTask, asynq.Queue("default"), asynq.Timeout(2*time.Hour)); err != nil {
		log.Fatalf("Failed to enqueue fetch reports task: %v", err)
	}

	go func() {
		log.Println("Starting Asynq scheduler...")
		if err := scheduler.Run(); err != nil {
			log.Fatalf("Could not run Asynq scheduler: %v", err)
		}
	}()

	go func() {
		log.Println("Starting Asynq worker server...")
		if err := srv.Run(mux); err != nil {
			log.Fatalf("Could not run Asynq worker server: %v", err)
		}
	}()

	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)

	<-quit

	log.Println("Shutdown signal received, shutting down gracefully...")

	scheduler.Shutdown()
	log.Println("Asynq scheduler shut down.")

	srv.Shutdown()
	log.Println("Asynq worker server shut down.")

	asynqClient.Close()
	log.Println("Asynq client closed.")

	log.Println("Worker process shut down complete.")
}

func deleteTasksByType(inspector *asynq.Inspector, queue, taskType string) (int, error) {
	listFns := []func(string, ...asynq.ListOption) ([]*asynq.TaskInfo, error){
		inspector.ListPendingTasks,
		inspector.ListScheduledTasks,
		inspector.ListRetryTasks,
		inspector.ListArchivedTasks,
	}

	total := 0
	for _, listFn := range listFns {
		tasks, err := listAllTasks(queue, listFn)
		if err != nil {
			return total, err
		}
		for _, task := range tasks {
			if task.Type != taskType {
				continue
			}
			if err := inspector.DeleteTask(queue, task.ID); err != nil {
				return total, err
			}
			total++
		}
	}

	return total, nil
}

func listAllTasks(queue string, listFn func(string, ...asynq.ListOption) ([]*asynq.TaskInfo, error)) ([]*asynq.TaskInfo, error) {
	const pageSize = 100
	var all []*asynq.TaskInfo
	page := 1
	for {
		tasks, err := listFn(queue, asynq.Page(page), asynq.PageSize(pageSize))
		if err != nil {
			return nil, err
		}
		if len(tasks) == 0 {
			break
		}
		all = append(all, tasks...)
		if len(tasks) < pageSize {
			break
		}
		page++
	}
	return all, nil
}
