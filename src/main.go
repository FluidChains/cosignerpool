package main

import (
	"os"
	"io"
	"time"
	"context"
	"log"
	"net"

	"github.com/bradfitz/gomemcache/memcache"

	"google.golang.org/grpc"
	codes "google.golang.org/grpc/codes"
	status "google.golang.org/grpc/status"
	pb "github.com/FluidChains/cosignerpool/proto"
)

var mc *memcache.Client
var err error

const (
	port = "0.0.0.0:50051"
)

type server struct {
	pb.UnimplementedCosignerpoolServer
}

func (s *server) Put(ctx context.Context, in *pb.PutRequest) (*pb.PutResponse, error) {
	var err = mc.Set(&memcache.Item{Key: string(in.GetKey()), Value: []byte(in.GetValue()), Expiration: in.GetExpiration()})
	if err != nil {
            log.Printf("gRpc error: %v", err.Error())
            return nil, status.Errorf(codes.NotFound, err.Error())
        }
	log.Printf("Inserted: %v:%v", in.GetKey(), in.GetValue())
	return &pb.PutResponse{Success: true}, nil
}

func (s *server) Get(ctx context.Context, in *pb.GetRequest) (*pb.GetResponse, error) {
	var it, err = mc.Get(string(in.GetKey()))
	if err != nil {
            log.Printf("gRpc error: %v", err.Error())
            return nil, status.Errorf(codes.NotFound, err.Error())
        }
	log.Printf("Retrieved: %v", in.GetKey())
	return &pb.GetResponse{Value: string(it.Value)}, nil
}

func (s *server) Delete(ctx context.Context, in *pb.DeleteRequest) (*pb.DeleteResponse, error) {
	var err = mc.Delete(string(in.GetKey()))
	if err != nil {
            log.Printf("gRpc error: %v", err.Error())
            return nil, status.Errorf(codes.NotFound, err.Error())
        }
	log.Printf("Deleted: %v", in.GetKey())
	return &pb.DeleteResponse{Success: true}, nil
}

func (s *server) Ping(ctx context.Context, in *pb.Empty) (*pb.Pong, error) {
	log.Printf("Ping")
        return &pb.Pong{Message: "Pong"}, nil
}

func (s *server) GetTime(ctx context.Context, in *pb.Empty) (*pb.GetTimeResponse, error) {
	var timestamp int32 = int32(time.Now().Unix())
        return &pb.GetTimeResponse{Timestamp: timestamp}, nil
}

func main() {
        _ = os.Mkdir("log", 0755)
        f, err := os.OpenFile("log/access.log", os.O_RDWR | os.O_CREATE | os.O_APPEND, 0666)
        if err != nil {
            log.Fatalf("error opening file: %v", err)
        }
        defer f.Close()

        mw := io.MultiWriter(os.Stdout, f)
        log.SetOutput(mw)
        log.Printf("Starting Cosignerpool server")

	mc = memcache.New("memcached:11211")

	lis, err := net.Listen("tcp", port)
	if err != nil {
		log.Fatalf("failed to listen: %v", err)
	}

	s := grpc.NewServer()
	pb.RegisterCosignerpoolServer(s, &server{})
	if err := s.Serve(lis); err != nil {
		log.Fatalf("failed to serve: %v", err)
	}
}
