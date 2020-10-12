# kerbal
DRL experiments with Kerbal Space Program

Based on Whiteaster solution:
https://medium.com/@whiteastercom/kerbal-space-program-complex-environment-for-reinforcement-learning-12318db065f5


Environment: Game + KRPC
https://krpc.github.io/krpc/


## Docker instructions for Distributed execution

After clonin the repo
```
docker build -t mad_rl/kerbal:0.1 .
```

Once you already have the docker container built in your local registry, you can run the follwoing command

```
docker run --network host --env-file .local.env --env-file .settings.env --env AGENT_MODE=test mad_rl/kerbal:0.1
```

in order to config your won MongoDB, RabbitMQ and InfluxDB edit the file .local.env