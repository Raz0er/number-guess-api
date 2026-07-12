output "instance_id" {
  description = "EC2 instance identifier"
  value       = aws_instance.app.id
}

output "public_ip" {
  description = "Public IPv4 address of the EC2 instance"
  value       = aws_instance.app.public_ip
}

output "public_url" {
  description = "Public URL of the application"
  value       = "http://${aws_instance.app.public_ip}"
}

output "ssh_command" {
  description = "Command used to connect to the EC2 instance"
  value       = "ssh ec2-user@${aws_instance.app.public_ip}"
}
output "github_actions_role_arn" {
  description = "IAM role ARN used by GitHub Actions through OIDC"
  value       = aws_iam_role.github_actions.arn
}
output "cloudwatch_log_group_name" {
  description = "CloudWatch Logs group containing application logs"
  value       = aws_cloudwatch_log_group.app.name
}
