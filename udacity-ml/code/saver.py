import tensorflow as tf

# The file path to save the data
# 文件保存路径
save_file = './model.ckpt'

# Two Tensor Variables: weights and bias
# 两个 Tensor 变量：权重和偏置项
weights = tf.Variable(tf.truncated_normal([2, 3]))
bias = tf.Variable(tf.truncated_normal([3]))

# Class used to save and/or restore Tensor Variables
# 用来存取 Tensor 变量的类
saver = tf.train.Saver()

with tf.Session() as sess:
    # Initialize all the Variables
    # 初始化所有变量
    sess.run(tf.global_variables_initializer())

    # Show the values of weights and bias
   # 显示变量和权重
    print('Weights:')
    print(sess.run(weights))
    print('Bias:')
    print(sess.run(bias))

    # Save the model
    # 保存模型
    saver.save(sess, save_file)