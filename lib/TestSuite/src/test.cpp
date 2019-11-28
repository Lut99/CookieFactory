#include <iostream>

using namespace std;

template <typename T> void *to_pointer(T elem) {
    T *p = new T;
    (*p) = elem;
    return static_cast<void*>(p);
}
template <typename T> T from_pointer(void *p) {
    // Cast and return
    return (*(static_cast<T*>(p)));
}
template <typename T> void delete_pointer(void *p) {
    // Cast and delete
    delete static_cast<T*>(p);
}

int main() {
    string test = "Hello, there!";
    void *p = to_pointer(test);
    // Print the returned value
    cout << from_pointer<string>(p) << endl;

    // Delete
    delete_pointer<string>(p);

    return 0;
}