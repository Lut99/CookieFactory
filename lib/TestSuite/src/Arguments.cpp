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

Arguments::Arguments() {
    /* Case for no arguments */

    // Just initialize the required variables
    this->size = 0;
    this->max_size = 0;
    this->args = NULL;
}
template <typename T> Arguments::Arguments(string key, T value) {
    /* Case for one argument */

    // First of all, initialize the required variables
    this->size = 0;
    this->max_size = 1;
    this->args = new Arg[1];

    // Next, use the basecase from the recursive function to add all the argument
    this->store_pairs(key, value);
}
template <typename T, class ... Types> Arguments::Arguments(string key, T value, Types... args) {
    /* Case for more arguments */

    // First of all, initialize the required variables
    this->size = 0;
    this->max_size = sizeof...(args) + 1;
    this->args = new Arg[1];

    // Next, use the recursive function to add all arguments
    this->store_pairs(key, value, args...);
}
Arguments::~Arguments() {
    // Cleanup the array
    delete[] this->args;
}

template <typename T> void Arguments::_store_pair(string key, T value) {
    // Fill the arg struct
    this->args[this->size].key = key;
    this->args[this->size].value = static_cast<void*>(&value);
    this->args[this->size].type = typeid(T).hash_code();
    // Also save the type code
    const char* type_name = typeid(T).name();
    stringstream sstr;
    for (int i = 0; type_name[i] != '\0'; i++) {
        sstr << type_name[i];
    }
    this->args[this->size].type_name = sstr.str();

    // Increment the size
    this->size++;
}
template <typename T> void Arguments::store_pairs(string key, T value) {
    /* Base case for recursive function */

    // Check if string already exists
    for (int i = 0; i < this->size; i++) {
        if (this->args[i].key.compare(key) == 0) {
            throw runtime_error("Duplicate key \"" + key + "\"");
        }
    }

    // Add key and the value
    this->_store_pair(key, value);
}
template <typename T, class ... Types> void Arguments::store_pairs(string key, T value, Types... args) {
    /* Recursive case for recursive function */

    // Check if string already exists
    for (int i = 0; i < this->size; i++) {
        if (this->args[i].key.compare(key) == 0) {
            throw runtime_error("Duplicate key \"" + key + "\"");
        }
    }

    // Add key and the value
    this->_store_pair(key, value);

    // Do the rest
    this->store_pairs(args...);
}

template <typename T> void Arguments::add_arg(string key, T value) {
    // First, check for duplicates
    for (int i = 0; i < this->size; i++) {
        if (this->args[i].key.compare(key) == 0) {
            // There is a duplicate
            throw runtime_error("Duplicate key \"" + key + "\"");
        }
    }

    // Check if we should resize
    if (this->size == this->max_size - 1) {
        // We do, so resize it to +1 (since there won't be many elements anyway)
        int new_max_size = this->max_size + 1;
        Arg *new_args = new Arg[new_max_size];

        // Copy the old array
        for (int i = 0; i < this->max_size; i++) {
            new_args[i] = this->args[i];
        }

        // Delete the old one
        delete[] this->args;

        // Set the new array & size
        this->args = new_args;
        this->max_size = new_max_size;
    }
    
    // Set the new value
    this->_store_pair(key, value);
}

template <typename T> T Arguments::get (string key) {
    // Search for element with given key
    for (int i = 0; i < this->size; i++) {
        if (this->args[i].key.compare(key) == 0) {
            // Check if the type compares
            if (this->args[i].type != typeid(T).hash_code()) {
                throw runtime_error("Key \"" + key + "\" has type \"" + this->args[i].type_name + "\", but got type \"" + typeid(T).name() + "\"");
            }
            // Return the object matching to the value
            return (*(static_cast<T*>(this->args[i].value)));
        }
    }
    // Not found
    throw runtime_error("Unknown key \"" + key + "\"");
}


void* test(void* arg) {
    return arg;
}

template <typename T> void* to_pointer (T input) {
    // Store it in memory
    T* mem = new T;
    (*mem) = input;
    return (void*) mem;
}
template <typename T> T from_pointer(void* input) {
    return (*((string*) input));
}


int main() {
    string name = "Carl";
    int age = 19;
    Arguments args = Arguments("name", name, "age", age);
    cout << args.get<string>("name") << ", " << args.get<int>("age") << endl;
}