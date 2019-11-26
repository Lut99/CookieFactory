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
    this->size = tuple_size<Types>::value;

    // Init the keys array to NULL
    this->keys = NULL;

    // Put the values in the tuple
    this->values = tuple<Types...>(values);
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
template <typename ... Types> void Arguments<Types...>::&operator[] (std::string key) {
    
}


int main() {
    cout << "Hello there!" << endl;

    Arguments<int, int> test = Arguments<int, int>(2, 5, 5);
}