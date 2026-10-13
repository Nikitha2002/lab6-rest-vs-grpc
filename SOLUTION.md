| Method | Local (ms) | Same-Zone (ms) | Different Region (ms) |
|---|---:|---:|---:|
| REST add | 2.192 | 3.160 | 467.498 |
| gRPC add | 0.516 | 1.009 | 150.907 |
| REST rawimg | 4.401 | 7.073 | 2036.314 |
| gRPC rawimg | 4.358 | 10.037 | 421.800 |
| REST dotproduct | 2.597 | 3.551 | 518.205 |
| gRPC dotproduct | 0.645 | 1.162 | 150.654 |
| REST jsonimg | 29.535 | 39.912 | 2009.185 |
| gRPC jsonimg | 23.167 | 34.464 | 460.377 |
| PING | 0.032 | 0.485 | 146.404 |

## Performance Observations

The results show that gRPC generally performed better than REST, particularly for lightweight operations and communication across regions. On localhost, gRPC add averaged 0.516 ms compared with 2.192 ms for REST. In the same-zone experiment, gRPC was faster for add, dotproduct, and jsonimage, although REST was slightly faster for rawimage.

Network latency had a significant impact on performance. Average ping latency increased from 0.032 ms on localhost to 0.485 ms within the same zone and 146.404 ms between Oregon and Frankfurt. In the different-region experiment, REST add averaged 467.498 ms compared with 150.907 ms for gRPC. REST generally creates a new TCP connection for each request in our client implementation, whereas gRPC reuses an HTTP/2 connection through a persistent channel. This makes connection overhead particularly noticeable when network round-trip times are high.

Image operations were more expensive than lightweight operations because they transmit much larger payloads. Base64 encoding also increases the transmitted data size and adds encoding and decoding overhead. Overall, these measurements demonstrate that network distance, connection reuse, serialization, and payload size all influence RPC performance.
