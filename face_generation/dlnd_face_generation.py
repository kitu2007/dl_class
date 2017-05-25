
# coding: utf-8

# # Face Generation
# In this project, you'll use generative adversarial networks to generate new images of faces.
# ### Get the Data
# You'll be using two datasets in this project:
# - MNIST
# - CelebA
# 
# Since the celebA dataset is complex and you're doing GANs in a project for the first time, we want you to test your neural network on MNIST before CelebA.  Running the GANs on MNIST will allow you to see how well your model trains sooner.
# 
# If you're using [FloydHub](https://www.floydhub.com/), set `data_dir` to "/input" and use the [FloydHub data ID](http://docs.floydhub.com/home/using_datasets/) "R5KrjnANiKVhLWAkpXhNBe".

# In[1]:

data_dir = './data'

# FloydHub - Use with data ID "R5KrjnANiKVhLWAkpXhNBe"
#data_dir = '/input'


"""
DON'T MODIFY ANYTHING IN THIS CELL
"""
import helper
import os
import pickle as pkl 
helper.download_extract('mnist', data_dir)
helper.download_extract('celeba', data_dir)


# ## Explore the Data
# ### MNIST
# As you're aware, the [MNIST](http://yann.lecun.com/exdb/mnist/) dataset contains images of handwritten digits. You can view the first number of examples by changing `show_n_images`. 

# In[2]:

show_n_images = 25

"""
DON'T MODIFY ANYTHING IN THIS CELL
"""
#get_ipython().magic('matplotlib inline')
import os
from glob import glob
from matplotlib import pyplot
import ipdb
from IPython import embed
pyplot.ion()

mnist_images = helper.get_batch(glob(os.path.join(data_dir, 'mnist/*.jpg'))[:show_n_images], 28, 28, 'L')
pyplot.imshow(helper.images_square_grid(mnist_images, 'L'), cmap='gray')


# ### CelebA
# The [CelebFaces Attributes Dataset (CelebA)](http://mmlab.ie.cuhk.edu.hk/projects/CelebA.html) dataset contains over 200,000 celebrity images with annotations.  Since you're going to be generating faces, you won't need the annotations.  You can view the first number of examples by changing `show_n_images`.

# In[3]:

show_n_images = 25

"""
DON'T MODIFY ANYTHING IN THIS CELL
"""
mnist_images = helper.get_batch(glob(os.path.join(data_dir, 'img_align_celeba/*.jpg'))[:show_n_images], 28, 28, 'RGB')
pyplot.imshow(helper.images_square_grid(mnist_images, 'RGB'))


# ## Preprocess the Data
# Since the project's main focus is on building the GANs, we'll preprocess the data for you.  The values of the MNIST and CelebA dataset will be in the range of -0.5 to 0.5 of 28x28 dimensional images.  The CelebA images will be cropped to remove parts of the image that don't include a face, then resized down to 28x28.
# 
# The MNIST images are black and white images with a single [color channel](https://en.wikipedia.org/wiki/Channel_(digital_image%29) while the CelebA images have [3 color channels (RGB color channel)](https://en.wikipedia.org/wiki/Channel_(digital_image%29#RGB_Images).
# ## Build the Neural Network
# You'll build the components necessary to build a GANs by implementing the following functions below:
# - `model_inputs`
# - `discriminator`
# - `generator`
# - `model_loss`
# - `model_opt`
# - `train`
# 
# ### Check the Version of TensorFlow and Access to GPU
# This will check to make sure you have the correct version of TensorFlow and access to a GPU

# In[4]:

"""
DON'T MODIFY ANYTHING IN THIS CELL
"""
from distutils.version import LooseVersion
import warnings
import tensorflow as tf

# Check TensorFlow Version
assert LooseVersion(tf.__version__) >= LooseVersion('1.0'), 'Please use TensorFlow version 1.0 or newer.  You are using {}'.format(tf.__version__)
print('TensorFlow Version: {}'.format(tf.__version__))

# Check for a GPU
if not tf.test.gpu_device_name():
    warnings.warn('No GPU found. Please use a GPU to train your neural network.')
else:
    print('Default GPU Device: {}'.format(tf.test.gpu_device_name()))


# ### Input
# Implement the `model_inputs` function to create TF Placeholders for the Neural Network. It should create the following placeholders:
# - Real input images placeholder with rank 4 using `image_width`, `image_height`, and `image_channels`.
# - Z input placeholder with rank 2 using `z_dim`.
# - Learning rate placeholder with rank 0.
# 
# Return the placeholders in the following the tuple (tensor of real input images, tensor of z data)

# In[5]:

import problem_unittests as tests

def model_inputs(image_width, image_height, image_channels, z_dim):
    """
    Create the model inputs
    :param image_width: The input image width
    :param image_height: The input image height
    :param image_channels: The number of image channels
    :param z_dim: The dimension of Z
    :return: Tuple of (tensor of real input images, tensor of z data, learning rate)
    """
    # TODO: Implement Function
    real_input = tf.placeholder(tf.float32,shape=(None, image_width, image_height, image_channels),name='real_input')
    tensor_z = tf.placeholder(tf.float32, shape=(None,z_dim),name='random_z')
    learning_rate = tf.placeholder(tf.float32,name='lr')
    return real_input, tensor_z, learning_rate


"""
DON'T MODIFY ANYTHING IN THIS CELL THAT IS BELOW THIS LINE
"""
tests.test_model_inputs(model_inputs)


# ### Discriminator
# Implement `discriminator` to create a discriminator neural network that discriminates on `images`.  This function should be able to reuse the variabes in the neural network.  Use [`tf.variable_scope`](https://www.tensorflow.org/api_docs/python/tf/variable_scope) with a scope name of "discriminator" to allow the variables to be reused.  The function should return a tuple of (tensor output of the discriminator, tensor logits of the discriminator).

# In[6]:

def discriminator(images, reuse=False, is_train=True):
    """
    Create the discriminator network
    :param image: Tensor of input image(s)
    :param reuse: Boolean if the weights should be reused
    :return: Tuple of (tensor output of the discriminator, tensor logits of the discriminator)
    """
    with tf.variable_scope('discriminator', reuse=reuse) as scope:
        # input is 28X28X3
        alpha = 0.2
        x = tf.layers.conv2d(images,32,(5,5),strides=(2,2), activation=None, padding='same')
        x = tf.maximum(alpha*x,x)
        # x is 14X14X32
        x = tf.layers.conv2d(x,64,(5,5),strides=(2,2), activation=None, padding='same')
        x = tf.layers.batch_normalization(x, training=is_train)
        x = tf.maximum(alpha*x,x)
        # x is 7X7X64
        x = tf.layers.conv2d(x,128,(5,5),strides=(2,2), activation=None, padding='same')
        x = tf.layers.batch_normalization(x, training=is_train)
        x = tf.maximum(alpha*x,x)
        # x is 4X4X128

        flat = tf.reshape(x, (-1, 4*4*128))
        logits = tf.layers.dense(flat,1)
        out = tf.nn.sigmoid(logits)
    return out, logits


"""
DON'T MODIFY ANYTHING IN THIS CELL THAT IS BELOW THIS LINE
"""
tests.test_discriminator(discriminator, tf)


# ### Generator
# Implement `generator` to generate an image using `z`. This function should be able to reuse the variabes in the neural network.  Use [`tf.variable_scope`](https://www.tensorflow.org/api_docs/python/tf/variable_scope) with a scope name of "generator" to allow the variables to be reused. The function should return the generated 28 x 28 x `out_channel_dim` images.

# In[7]:

def generator(z, out_channel_dim, is_train=True):
    """
    Create the generator network
    :param z: Input z
    :param out_channel_dim: The number of channels in the output image
    :param is_train: Boolean if generator is being used for training
    :return: The tensor output of the generator
    """
    alpha = 0.2
    in_channels = 512
    with tf.variable_scope('generator', reuse= (not is_train)) as scope:
        # TODO: Implement Function
        # z is a one dimensional random vector
        x = tf.layers.dense(z, 4*4*in_channels)
        x = tf.reshape(x,(-1, 4, 4, in_channels))
        x = tf.layers.batch_normalization(x, training=is_train, center=False, scale=False)
        x = tf.maximum(alpha*x, x)
        # 4*4*in_channels

        x = tf.layers.conv2d_transpose(x, int(in_channels/2), (5,5),(2,2),padding='same')
        x = tf.layers.batch_normalization(x, training=is_train, center=False, scale=False)
        x = tf.maximum(alpha*x, x)
        # 8*8*in_channels/2        - 512

        x1 = tf.slice(x,[0,1,1,0],[-1,-1,-1,-1])
        # 7*7*in_channels/2        

        x1 = tf.layers.conv2d_transpose(x1,int(in_channels/4),(5,5),(2,2),padding='same')
        x1 = tf.layers.batch_normalization(x1, training=is_train, center=False, scale=False)
        x1 = tf.maximum(alpha*x1, x1)
        # 14*14*in_channels/2  - 256
        if in_channels>512:
            x1 = tf.layers.conv2d_transpose(x1,int(in_channels/8),(5,5),(2,2),padding='same')
            x1 = tf.layers.batch_normalization(x1, training=is_train, center=False, scale=False)
            x1 = tf.maximum(alpha*x1, x1)
            x1 = tf.layers.conv2d_transpose(x1, out_channel_dim,(5,5),(1,1),padding='same')
            # 28*28*in_channels/2  - 128
        else:
            x1 = tf.layers.conv2d_transpose(x1, out_channel_dim,(5,5),(2,2),padding='same')
            # 28X28* 128
        
        out = tf.tanh(x1)
    
    return out


"""
DON'T MODIFY ANYTHING IN THIS CELL THAT IS BELOW THIS LINE
"""
#tests.test_generator(generator, tf)


# ### Loss
# Implement `model_loss` to build the GANs for training and calculate the loss.  The function should return a tuple of (discriminator loss, generator loss).  Use the following functions you implemented:
# - `discriminator(images, reuse=False)`
# - `generator(z, out_channel_dim, is_train=True)`

# In[8]:

def model_loss(input_real, input_z, out_channel_dim):
    """
    Get the loss for the discriminator and generator
    :param input_real: Images from the real dataset
    :param input_z: Z input
    :param out_channel_dim: The number of channels in the output image
    :return: A tuple of (discriminator loss, generator loss)
    """
    real_out, real_logits = discriminator(input_real, reuse=False)
    fake_image = generator(input_z, out_channel_dim, is_train=True)
    fake_out, fake_logits = discriminator(fake_image, reuse=True)
    smooth = 0.9
    d_real_loss = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(logits = real_logits, labels = tf.ones_like(real_logits)*smooth))
    d_fake_loss = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(logits = fake_logits, labels = tf.zeros_like(fake_logits)))
    d_loss = d_real_loss + d_fake_loss
    
    g_loss = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(logits = fake_logits, labels = tf.ones_like(fake_logits)))
    
    return d_loss, g_loss


"""
DON'T MODIFY ANYTHING IN THIS CELL THAT IS BELOW THIS LINE
"""
tests.test_model_loss(model_loss)


# ### Optimization
# Implement `model_opt` to create the optimization operations for the GANs. Use [`tf.trainable_variables`](https://www.tensorflow.org/api_docs/python/tf/trainable_variables) to get all the trainable variables.  Filter the variables with names that are in the discriminator and generator scope names.  The function should return a tuple of (discriminator training operation, generator training operation).

# In[9]:

def model_opt(d_loss, g_loss, learning_rate, beta1):
    """
    Get optimization operations
    :param d_loss: Discriminator loss Tensor
    :param g_loss: Generator loss Tensor
    :param learning_rate: Learning Rate Placeholder
    :param beta1: The exponential decay rate for the 1st moment in the optimizer
    :return: A tuple of (discriminator training operation, generator training operation)
    """
    # TODO: Implement Function
    t_vars = tf.trainable_variables()
    d_vars = [var for var in t_vars if var.name.startswith('discriminator')]
    g_vars = [var for var in t_vars if var.name.startswith('generator')]
    
    with tf.control_dependencies(tf.get_collection(tf.GraphKeys.UPDATE_OPS)):
        d_train_opt = tf.train.AdamOptimizer(learning_rate=learning_rate, beta1=beta1).minimize(d_loss,var_list = d_vars)
        g_train_opt = tf.train.AdamOptimizer(learning_rate=learning_rate, beta1=beta1).minimize(g_loss,var_list = g_vars)
    
    return d_train_opt, g_train_opt


"""
DON'T MODIFY ANYTHING IN THIS CELL THAT IS BELOW THIS LINE
"""
tests.test_model_opt(model_opt, tf)


# ## Neural Network Training
# ### Show Output
# Use this function to show the current output of the generator during training. It will help you determine how well the GANs is training.

# In[10]:

"""
DON'T MODIFY ANYTHING IN THIS CELL
"""
import numpy as np

def show_generator_output(sess, n_images, input_z, out_channel_dim, image_mode):
    """
    Show example output for the generator
    :param sess: TensorFlow session
    :param n_images: Number of Images to display
    :param input_z: Input Z Tensor
    :param out_channel_dim: The number of channels in the output image
    :param image_mode: The mode to use for images ("RGB" or "L")
    """
    cmap = None if image_mode == 'RGB' else 'gray'
    z_dim = input_z.get_shape().as_list()[-1]
    example_z = np.random.uniform(-1, 1, size=[n_images, z_dim])

    samples = sess.run(
        generator(input_z, out_channel_dim, False),
        feed_dict={input_z: example_z})
    
    #ipdb.set_trace()
    images_grid = helper.images_square_grid(samples, image_mode)
    pyplot.imshow(images_grid, cmap=cmap)
    pyplot.show()
    return samples


# ### Train
# Implement `train` to build and train the GANs.  Use the following functions you implemented:
# - `model_inputs(image_width, image_height, image_channels, z_dim)`
# - `model_loss(input_real, input_z, out_channel_dim)`
# - `model_opt(d_loss, g_loss, learning_rate, beta1)`
# 
# Use the `show_generator_output` to show `generator` output while you train. Running `show_generator_output` for every batch will drastically increase training time and increase the size of the notebook.  It's recommended to print the `generator` output every 100 batches.

# In[11]:

def train(epoch_count, batch_size, z_dim, learning_rate, beta1, get_batches, data_shape, data_image_mode):
    """
    Train the GAN
    :param epoch_count: Number of epochs
    :param batch_size: Batch Size
    :param z_dim: Z dimension
    :param learning_rate: Learning Rate
    :param beta1: The exponential decay rate for the 1st moment in the optimizer
    :param get_batches: Function to get batches
    :param data_shape: Shape of the data
    :param data_image_mode: The image mode to use for images ("RGB" or "L")
    """
    # TODO: Build Model
    ckpt_dir = './checkpoint'
    if not os.path.exists(ckpt_dir):
        os.makedirs(ckpt_dir)
       
    show_every = 100 # show every 1000 iter
    num_train_examples = data_shape[0]
    image_width = data_shape[1]
    image_height = data_shape[2]
    image_channels = data_shape[3]
    sample_z = np.random.uniform(-1,1,size=(batch_size,z_dim))

    # defined the net here
    input_real, input_z, learning_rate_ph = model_inputs(image_width, image_height, image_channels,z_dim)
    d_loss, g_loss = model_loss(input_real, input_z, image_channels )
    d_train_opt, g_train_opt = model_opt(d_loss, g_loss, learning_rate_ph, beta1)

    saver = tf.train.Saver()
    counter = 0
    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        #samples = sess.run(generator(input_z, image_channels, False), feed_dict={input_z:np.random.uniform(-1, 1, size=[batch_size, z_dim])})
        # images1 = next(get_batches(batch_size))
        # samples = sess.run(discriminator(input_real,True), feed_dict={input_real:images1})
        for epoch_i in range(epoch_count):
            generated_sample_list = []
            for iter, batch_images in enumerate(get_batches(batch_size)):
                batch_z = np.random.uniform(-1,1,size=(batch_size,z_dim))
                counter +=1
                # TODO: Train Model
                if iter % 5 == 0:
                    _, d_loss_val = sess.run([d_train_opt, d_loss],feed_dict =
                                             {input_real:batch_images,
                                              input_z: batch_z,
                                             learning_rate_ph:learning_rate})

                _, g_loss_val = sess.run([g_train_opt, g_loss],feed_dict={input_real:batch_images,
                                                  input_z: batch_z,
                                                  learning_rate_ph:learning_rate})
                if counter % 10 == 0:
                    print ('epoch:{} iter:{} counter:{} d_loss:{} g_loss:{}'.format(epoch_i, iter, counter, d_loss_val, g_loss_val))

                if show_every > 0 and counter % show_every == 0:
                    n_images = 16
                    generated_samples = show_generator_output(sess, n_images, input_z, image_channels, data_image_mode)
                    generated_sample_list.append((epoch_i, counter, generated_samples))
            
            ckpt = '{}/generator_epoch_{}.ckpt'.format(ckpt_dir,epoch_i)
            saver.save(sess, ckpt)
            with open('samples{}.pkl'.format(epoch_i), 'wb') as fp:
                pkl.dump(generated_sample_list,fp)
    
# ### MNIST
# Test your GANs architecture on MNIST.  After 2 epochs, the GANs should be able to generate images that look like handwritten digits.  Make sure the loss of the generator is lower than the loss of the discriminator or close to 0.

# In[13]:

batch_size = 128
z_dim = 100
learning_rate = 0.0002
beta1 = 0.5


"""
DON'T MODIFY ANYTHING IN THIS CELL THAT IS BELOW THIS LINE
"""
do_train = True
epochs = 2
mnist_dataset = helper.Dataset('mnist', glob(os.path.join(data_dir, 'mnist/*.jpg')))
if do_train:
    with tf.Graph().as_default():
        train(epochs, batch_size, z_dim, learning_rate, beta1, mnist_dataset.get_batches,
              mnist_dataset.shape, mnist_dataset.image_mode)
    

def inference(ckpt, batch_size, z_dim, get_batches, data_shape, data_image_mode):

    show_every = 1 # show every 1000 iter
    num_train_examples = data_shape[0]
    image_width = data_shape[1]
    image_height = data_shape[2]
    image_channels = data_shape[3]
    sample_z = np.random.uniform(-1,1,size=(batch_size,z_dim))
    generated_sample_list = []

    # defined the net here
    input_real, input_z, learning_rate_ph = model_inputs(image_width, image_height, image_channels,z_dim)
    d_loss, g_loss = model_loss(input_real, input_z, image_channels )
    d_train_opt, g_train_opt = model_opt(d_loss, g_loss, learning_rate_ph, beta1)

    saver = tf.train.Saver()
    counter = 0
    n_images = 10
    with tf.Session() as sess:
        saver.restore(sess, ckpt)
        print ('Model restored')        
        generated_samples = show_generator_output(sess, n_images, input_z, image_channels, data_image_mode)
        generated_sample_list.append((0, counter, generated_samples))
        #ipdb.set_trace()

if not do_train:
    with tf.Graph().as_default():
        ckpt1 = './checkpoint/generator_epoch_0.ckpt'
        inference(ckpt1, batch_size, z_dim, mnist_dataset.get_batches, mnist_dataset.shape, mnist_dataset.image_mode)

if 0:
    # ### CelebA
    # Run your GANs on CelebA.  It will take around 20 minutes on the average GPU to run one epoch.  You can run the whole epoch or stop when it starts to generate realistic faces.

    # In[ ]:

    batch_size = None
    z_dim = None
    learning_rate = None
    beta1 = None


    """
    DON'T MODIFY ANYTHING IN THIS CELL THAT IS BELOW THIS LINE
    """
    epochs = 1

    celeba_dataset = helper.Dataset('celeba', glob(os.path.join(data_dir, 'img_align_celeba/*.jpg')))
    with tf.Graph().as_default():
        train(epochs, batch_size, z_dim, learning_rate, beta1, celeba_dataset.get_batches,
              celeba_dataset.shape, celeba_dataset.image_mode)


    # ### Submitting This Project
    # When submitting this project, make sure to run all the cells before saving the notebook. Save the notebook file as "dlnd_face_generation.ipynb" and save it as a HTML file under "File" -> "Download as". Include the "helper.py" and "problem_unittests.py" files in your submission.
