/* INHERITANCE_TEST.c
 *   by tHE iNCREDIBLE mACHINE
 * 
 * DECRIPTION: Test file for checking struct inheritance
 */

#include <stdlib.h>
#include <stdio.h>

typedef struct {
    unsigned char type0;
    unsigned char type1;
} Parent;

typedef struct {
    Parent base;
    int prop3;
} Child;

typedef struct {
    Parent base;
    int prop4;
} Child2;

void print_prop(Parent *p) {
    // Find out what type it is
    if (p->type0 == 0) {
        // Cast back to child
        Child *c_back = (Child *)p;
        printf("%i\n", c_back->prop3);
    } else if (p->type0 == 1) {
        // Cast to child 2
        Child2 *c_back = (Child2 *)p;
        printf("%i\n", c_back->prop4);
    }
}

int main () {
    // Create the child struct and try to access the parent's
    Child *c = malloc(sizeof(Child));
    c->base.type0 = 0;
    c->base.type1 = 0;
    c->prop3 = 42;
    Child2 *c2 = malloc(sizeof(Child2));
    c2->base.type0 = 1;
    c2->base.type1 = 3;
    c2->prop4 = 69;
    // Cast to parent
    Parent *p = (Parent *)c;
    Parent *p2 = (Parent *)c2;
    print_prop(p);
    print_prop(p2);
    free(c);
    free(c2);
    return 0;
}