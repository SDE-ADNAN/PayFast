output "rds_endpoint" {
  value = aws_db_instance.payfast_postgres.endpoint
}

output "redis_endpoint" {
  value = aws_elasticache_cluster.payfast_redis.cache_nodes[0].address
}

output "ecs_cluster_name" {
  value = aws_ecs_cluster.payfast_cluster.name
}
