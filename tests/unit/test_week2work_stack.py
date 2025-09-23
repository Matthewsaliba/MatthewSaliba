import aws_cdk as core
import aws_cdk.assertions as assertions

from week2work_stack import Week2WorkStack

# example tests. To run these tests, uncomment this file along with the example
# resource in week2work/week2work_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = Week2WorkStack(app, "week2work")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
