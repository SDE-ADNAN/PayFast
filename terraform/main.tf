terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# 1. Network setup
resource "aws_vpc" "payfast_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  tags = { Name = "payfast-vpc" }
}

# 2. Database RDS cluster
resource "aws_db_subnet_group" "payfast_db_subnet" {
  name       = "payfast-database-subnets"
  subnet_ids = [] # In reality this takes aws_subnet.private[*].id
  tags = { Name = "payfast-db-subnets" }
}

resource "aws_db_instance" "payfast_postgres" {
  identifier           = "payfast-db"
  allocated_storage    = 20
  engine               = "postgres"
  engine_version       = "16"
  instance_class       = "db.t4g.micro"
  db_name              = "payfast_db"
  username             = "payfast"
  manage_master_user_password = true
  skip_final_snapshot  = true
  db_subnet_group_name = aws_db_subnet_group.payfast_db_subnet.name
}

# 3. Elasticache Redis
resource "aws_elasticache_cluster" "payfast_redis" {
  cluster_id           = "payfast-redis"
  engine               = "redis"
  node_type            = "cache.t4g.micro"
  num_cache_nodes      = 1
  parameter_group_name = "default.redis7"
  port                 = 6379
}

# 4. ECS Fargate Cluster
resource "aws_ecs_cluster" "payfast_cluster" {
  name = "payfast-cluster"
}

# Assume Service & Task Definition implementations map safely to target group ALBs.
