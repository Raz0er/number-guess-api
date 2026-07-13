data "aws_iam_openid_connect_provider" "github" {
  url = "https://token.actions.githubusercontent.com"
}

data "aws_iam_policy_document" "github_actions_assume_role" {
  statement {
    sid     = "AllowGitHubActionsAssumeRole"
    effect  = "Allow"
    actions = ["sts:AssumeRoleWithWebIdentity"]

    principals {
      type        = "Federated"
      identifiers = [data.aws_iam_openid_connect_provider.github.arn]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"
      values   = ["sts.amazonaws.com"]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:sub"

      values = [
        "repo:${var.github_owner}/${var.github_repository}:ref:refs/heads/${var.github_branch}"
      ]
    }
  }
}

resource "aws_iam_role" "github_actions" {
  name                 = "${var.project_name}-github-actions-role"
  assume_role_policy   = data.aws_iam_policy_document.github_actions_assume_role.json
  max_session_duration = 3600

  tags = {
    Name = "${var.project_name}-github-actions-role"
  }
}

data "aws_iam_policy_document" "github_actions_deploy" {
  statement {
    sid    = "SendCommandToApplicationInstance"
    effect = "Allow"

    actions = [
      "ssm:SendCommand"
    ]

    resources = [
      "arn:aws:ssm:${var.aws_region}::document/AWS-RunShellScript",
      aws_instance.app.arn
    ]
  }

  statement {
    sid    = "ReadCommandResult"
    effect = "Allow"

    actions = [
      "ssm:GetCommandInvocation"
    ]

    resources = ["*"]
  }

  statement {
    sid    = "DiscoverApplicationInstance"
    effect = "Allow"

    actions = [
      "ec2:DescribeInstances"
    ]

    resources = ["*"]
  }
}

resource "aws_iam_role_policy" "github_actions_deploy" {
  name   = "${var.project_name}-ssm-deploy-policy"
  role   = aws_iam_role.github_actions.id
  policy = data.aws_iam_policy_document.github_actions_deploy.json
}