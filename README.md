# local_lambda

Simple mechanism to run lambdas as if they were behind an API gateway

## Installation
```
$ pip install local_lambda
```

## Running
Create a configuration file named `.local-lambda.json` with a format simlar to this replacing with your funcitons and URLs

```
{
    "endpoints": {
        "/test": {
            "GET": {
                "function": "tests.functions.main.debug_me"
            },
            "POST": {
                "function": "tests.functions.main.debug_me"
            }
        }
    }
}
```

Run the following command:
```
$ local_lambda
```