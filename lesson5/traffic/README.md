# Testing

Images are 30x30 with 3 color channels (2700 input values)
Since I don't want to tweak all my hyperparams I'm locking some down.

**Constants:**
 - *Epochs:* 10
 - *Dense layer:* 128

## Results

| Conv Layers | Filters        | Pooling | Dropout  |Train Acc % | Train Loss | Test Acc % | Test Loss  | Notes                                                    |
| ----------- | -------------- | ------- | -------- |----------- | ---------- | -------    | ---------- | -------------------------------------------------------  |
| 1           | 16             | None    |  None    | 97.37      |  0.1385    | 87.11      |  1.0097    |  Overfitting                                             |
| 1           | 16             | 2x2 Max |  None    | 97.37      |  0.1339    | 92.40      |  0.5708    |                                                          |
| 1           | 32             | None    |  None    | 96.63      |  0.1690    | 89.58      |  0.7855    |  Overfitting                                             |
| 1           | 32             | 2x2 Max |  None    | 97.27      |  0.1330    | 93.85      |  0.5182    |                                                          |
| 2           | 16 → 32        | 2x2 Max |  None    | 97.73      |  0.0874    | 94.63      |  0.3289    |                                                          |
| 1           | 16             | None    |  0.3     | 5.60       |  3.5025    | 5.56       |  3.4927    |  Something broke                                         |
| 1           | 16             | 2x2 Max |  0.3     | 5.71       |  3.4952    | 5.52       |  3.5033    |  Similar to previous                                     |
| 1           | 32             | None    |  0.3     | 5.83       |  3.4987    | 5.33       |  3.4977    |                                                          |
| 1           | 32             | 2x2 Max |  0.3     | 30.69      |  2.5556    | 0.4103     |  2.2055    | A little better but still bad                            |
| 2           | 16 → 32        | 2x2 Max |  0.3     | 94.76      |  0.1894    | 92.54      |  0.2800    | A lot of improvements, almost as good as without dropout |
| 3           | 16 → 32 -> 64  | 2x2 Max |  0.3     | 95.86      |  0.1450    | 95.28      |  0.1811    | The best so farr                                         |
  
