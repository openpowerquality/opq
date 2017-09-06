#ifndef ACQUISITION_LOCKFREEQUEUE_H
#define ACQUISITION_LOCKFREEQUEUE_H

#include <queue>
#include <thread>
#include <mutex>
#include <condition_variable>


template <typename T>
/**
 * @brief A syncronized generic queue.
 * Thread-safe and backed by std::queue.
 */
class SyncQueue
{
public:

    /**
     * @brief Creates an empty queue.
     */
    SyncQueue(){
        _count = 0;
    }

    /**
     * @brief Pops an item off the top of the queue.
     * @return data item.
     */
    T pop()
    {
        std::unique_lock<std::mutex> mlock(_mutex);
        while (_queue.empty())
        {
            cond_.wait(mlock);
        }
        auto item = _queue.front();
        _queue.pop();
        _count--;
        return item;
    }

    /**
     * Pops an item off the top of the queue.
     * @param item data item.
     */
    void pop(T& item)
    {
        std::unique_lock<std::mutex> mlock(_mutex);
        while (_queue.empty())
        {
            cond_.wait(mlock);
        }
        item = _queue.front();
        _queue.pop();
        _count--;
    }

    /**
     * @brief Push an item onto the back of the queue.
     * @param item data item.
     */
    void push(const T& item)
    {
        std::unique_lock<std::mutex> mlock(_mutex);
        _queue.push(item);
        _count++;
        mlock.unlock();
        cond_.notify_one();

    }

    /**
     * @brief Push an item onto the back of the queue.
     * @param item data item.
     */
    void push(T&& item)
    {
        std::unique_lock<std::mutex> mlock(_mutex);
        _queue.push(std::move(item));
        _count++;
        mlock.unlock();
        cond_.notify_one();

    }

    /**
     * @brief remove all elements from the queue.
     */
    void clear(){
        std::unique_lock<std::mutex> mlock(_mutex);
        std::queue<T>().swap(_queue);
        _count = 0;


    }

    /**
     * @brief Current number of items in the queue.
     * Not thread safe, so it's more of a suggestion.
     * @return number of items in the queue.
     */
    size_t size(){
        return _count;
    }

private:
    std::queue<T> _queue;
    std::mutex _mutex;
    std::condition_variable cond_;
    size_t _count;
};

#endif //ACQUISITION_LOCKFREEQUEUE_H
