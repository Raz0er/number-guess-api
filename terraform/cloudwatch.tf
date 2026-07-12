resource "aws_cloudwatch_log_group" "app" {
  name              = "/number-guess-api/application"
  retention_in_days = 7

  tags = {
    Name = "${var.project_name}-application-logs"
  }
}

data "aws_iam_policy_document" "ec2_cloudwatch_logs" {
  statement {
    sid    = "WriteApplicationLogs"
    effect = "Allow"

    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]

    resources = [
      "${aws_cloudwatch_log_group.app.arn}:*"
    ]
  }
}

resource "aws_iam_role_policy" "ec2_cloudwatch_logs" {
  name   = "${var.project_name}-cloudwatch-logs-policy"
  role   = aws_iam_role.ec2_ssm.id
  policy = data.aws_iam_policy_document.ec2_cloudwatch_logs.json
}
