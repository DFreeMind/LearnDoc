# caffe 学习（一）：总览
## Blobs
blobs 是以一个 C 形式（C-contiguous fashion）的内存内存结构来存储的 N 维数组。blobs 中的数据格式为 `N(Numbers) × K(Channel) × H(H eight) × W(Width)`。以一组图片为例 N 表示一个批次中的图片数量，K 表示图片的通道数（RGB），H、W 表示图片的高宽。如：(2, 3, 3, 4) 表示批次中有两张图片，每张图片 3 个通道，3，高为 4，如下：
```python
[[[[ 76, 203,  75, 109],
     [ 10, 168, 225,  94],
     [ 15,  37,   2,  45]],

    [[ 79, 170, 132,  40],
     [120, 181, 173, 183],
     [184, 192,  71,  93]],

    [[ 89, 119, 103, 195],
     [224, 252,  16, 144],
     [243, 254,  76,  28]]],


   [[[220, 198, 184, 246],
     [ 95, 230,  35,   4],
     [225,  86, 206, 252]],

    [[192,  71,  45, 100],
     [  4,  99,  61, 244],
     [ 94,  30,  68,   1]],

    [[ 71,  39,   7,  13],
     [120,  25, 241, 206],
     [ 96,  66, 231,  55]]]]
```
blob 内存是以行为主的层次结构，因此最后或者最右侧的维度是变化最快的，也就是 W 是变化最快的。以行为基础与以列为基础的结构图如下：
![image](https://ws4.sinaimg.cn/large/69d4185bly1fvp3z3ysydj20f805ht9g.jpg)

那么上述值在内存中的结构如下图：
![image](https://ws3.sinaimg.cn/large/69d4185bly1fvpcxikg8hj20g8084abm.jpg)
若想获得(1, 1, 0, 3)位置（计数是从0开始，(0, 0 ,0 , 0)表示第一个位置 76 ），即图中红色位置 100 在物理内存中的索引，计算方式为 $((n * K + k) * H + h) * W + w$，其中的n、k、h、w 即1、1、0、3，因此 100 的实际物理内存索引为 $((1 * 3 + 1) * 3 + 0) * 4 + 3 = 51$。

C-contiguous fashion 的相关内容可参考：
- [What is the difference between contiguous and non-contiguous arrays?](https://stackoverflow.com/questions/26998223/what-is-the-difference-between-contiguous-and-non-contiguous-arrays)
- [what does C-contiguous fashion mean in caffe blob storage?](https://stackoverflow.com/questions/37597814/what-does-c-contiguous-fashion-mean-in-caffe-blob-storage)

caffe 的 blob 数据结构不尽可以用于图片数据，还可以用于其他类型的数据，如在多层感知机（multi-layer perceptron）中的全连接层，使用的是2维数据结构（shape(N,D)），在 caffe 中叫做 InnerProductLayer。

blob 数据的维度依据层的类型和配置而有所不同。如对于一个卷积层，含有 96 个 11×11空间维度 3输入的filter，那么 blob 的结构就为 96 × 3 × 11 × 11。对于含有 1000 个输出，1024 个输入的全连接层来说，blob 的结构为 1000 × 1024。

### 实现细节
blob 数据中保存了两块内容，一块是我们传入的普通数据，还有一块是这些数据的梯度（diff）。这些数据既可以存储在 CPU 上，也可以存储在 GPU 上，他们有两种不同的访问方式：常量方式（const way），值不可改变；可变方式，值可以改变：
```c
const Dtype* cpu_data() const;
Dtype* mutable_cpu_data();
```
GPU 和梯度与此类似。

之所以这么设计，是因为 Blob 使用了 SyncedMem 类来同步 CPU 与 GPU 之间的数据，以次来隐藏同步细节和最小化数据传输。Blob 数据复制检验代码：
```c
// Assuming that data are on the CPU initially, and we have a blob.
const Dtype* foo;
Dtype* bar;
foo = blob.gpu_data(); // data copied cpu->gpu.
foo = blob.cpu_data(); // no data copied since both have up-to-date contents.
bar = blob.mutable_gpu_data(); // no data copied.
// ... some operations ...
bar = blob.mutable_gpu_data(); // no data copied when we are still on GPU.
foo = blob.cpu_data(); // data copied gpu->cpu, since the gpu side has modified the data
foo = blob.gpu_data(); // no data copied since both have up-to-date contents
bar = blob.mutable_cpu_data(); // still no data copied.
bar = blob.mutable_gpu_data(); // data copied cpu->gpu.
bar = blob.mutable_cpu_data(); // data copied gpu->cpu.
```

## Layer
layer 是模型的本质，计算单元的基础。层卷积 filters、pool、应用非线性函数、normalize、加载数据、计算损失如 softmax 和 hinge。
layer 的结构如下：
![image](https://wx2.sinaimg.cn/large/69d4185bly1fvq8a6hsx0j207b07saa9.jpg)
每一层定义了三种重要的计算：setup、forward、backward
- Setup：初始化层和连接，在模型初始化的时候
- Forward：给定来自底部的输入，计算输出并送到顶部
- Backward：给出关于顶部输出的梯度计算对于输入的梯度，然后发送到底部。

forward、backward有两种实现，一个对于 CPU，一个对于 GPU。如果没有实现 GPU 版本，那么层就会回退到 CPU 函数作为后补选项。在做快速试验时这是非常方便的，虽然会带来额外的数据转换的代价（他的输入会被从 GPU 拷贝到 CPU，输出时又会从 CPU 拷贝会 GPU）
对于整个网络操作，层有两个关键的责任：一个forward pass，使用输入产生输出；一个 backward pass，使用输出的梯度来计算关于参数和输入的梯度，向前传播到更糟的层。

## Net
网络通过组合与自微分（auto-differentiation）定义了一个函数及其梯度。caffe 是端对端的机器学习引擎。
网络是在计算图（DAG directed acyclic graph）中被连接的一组 layer 。一个典型的网络开始于数据输入层，它从磁盘导入加载数据，结束于数据损失层，计算分裂或者重建（reconstruction）任务的目标。
网络定义为一组层，他们通过文本模型语言（plaintext modeling language）连接。一个简单的逻辑回归分类器定义如下：
```
name: "LogReg"
layer {
  name: "mnist"
  type: "Data"
  top: "data"
  top: "label"
  data_param {
    source: "input_leveldb"
    batch_size: 64
  }
}
layer {
  name: "ip"
  type: "InnerProduct"
  bottom: "data"
  top: "ip"
  inner_product_param {
    num_output: 2
  }
}
layer {
  name: "loss"
  type: "SoftmaxWithLoss"
  bottom: "ip"
  bottom: "label"
  top: "loss"
}
```
结构如下：
![image](https://ws4.sinaimg.cn/large/69d4185bly1fvqks08uf3j20a20a5mxm.jpg)
模型通过 Net::Init() 完成初始化，初始化主要做两件事情：通过穿件 blob 和 layer 来构建整个 DAG；调用layer 的 Setup 函数。

网络的构建对设备是不可知的，构建完成之后，网络运行在 CPU 还是 GPU 是通过设置定义在`Caffe::mode`中的单个开关和设置`Caffe::set_mode`来决定。CPU 与 GPU 的转换使无缝的，独立于模型的定义。






[参考]
- [CSDN - 浅读Caffe: Blobs, Layers, and Nets](https://blog.csdn.net/u010167269/article/details/51067296)
- [知乎 - Caffe教程系列之元素篇](https://zhuanlan.zhihu.com/p/23173215)






