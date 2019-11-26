/* ARGUMENTS.cpp
*    by tHE iNCREDIBLE mACHINE
*
*  A class that can store multiple arguments by string keys. Not the faster,
*    but very variable in what it can store.
**/

#include <iostream>
#include <sstream>
#include <tuple>
#include "Arguments.h"

using namespace std;
using namespace TestSuite;

template <typename T>
Arg<T>::Arg(string key, T value) {
    // Create a copy of the key
    stringstream sstr;
    for (int i = 0; i < key.length(); i++) {
        sstr << key[i];
    }
    // Store both the copy and the given value
    this->key = sstr.str();
    this->value = value;
}

template <typename T>
bool Arg<T>::matches(string key) {
    return this->key.compare(key) == 0;
}
template <typename T>
T Arg<T>::get() {
    // Return the inner value
    return this->value;
}

template <typename ... Types> Arguments<Types...>::Arguments(Types... values) {
    // Get the size
    this->size = tuple_size<Types...>::value;

    // Init the keys array to NULL
    this->keys = NULL;

    // Put the values in the tuple
    this->values = tuple<Types...>(values...);
}
template <typename ... Types> Arguments<Types...>::~Arguments() {
    // Dealloc the keys array if necessary
    if (this->keys != NULL) {
        delete[] this->keys;
    }
}
template <typename ... Types> void Arguments<Types...>::set_keys(string *keys) {
    // Simply copy the keys pointer
    this->keys = keys;
}
template <typename ... Types> void* Arguments<Types...>::get_elem(string key) {
    // Find the key in the keys list
    for (int i = 0; i < this->size; i++) {
        if (this->keys[i].compare(key) == 0) {
            // Found it, return a pointer to given value
            return (void*) &get<(size_t) i>(this->values);
        }
    }
    // Not found, return NULL
    return NULL;
}
template <typename ... Types> const std::type_info& Arguments<Types...>::get_type(string key) {
    // Find the key in the keys list
    for (int i = 0; i < this->size; i++) {
        if (this->keys[i].compare(key) == 0) {
            // Found it, return the typeid
            const size_t index = (size_t) i;
            return typeid(typename tuple_element<index, tuple<Types...>>::type);
        }
    }
    // Not found, return NULL
    return NULL;
}

template <typename T, class ... Types> T get_arg(Arguments<Types...> args, std::string key) {
    // First, obtain the value given the key
    void *val = args.get_elem(key);
    if (val == NULL) {
        // Nothing found
        throw "Arguments \"" + key + "\" not found";
    }
    // Check if given type is correct
    if (typeid(T) != args.get_type(key)) {
        throw "Argument \"" + key + "\" is not of given type";
    }
    // Now, return the casted version to the reference
    return (T) (*val);
}


int main() {
    cout << "Hello there!" << endl;

    Arguments<string, int, bool> args = Arguments<string, int, bool>("Hello there!", 5, false);
    args.set_keys(new string[3] {"name", "age", "smart"});
    // Print the third element
    cout << "args[2] = " << get_arg<bool>(args, "smart") << endl;
}