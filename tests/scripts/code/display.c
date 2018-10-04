/** Define a function to print using the C stdout.
 *
 * @author: Miguel Ramos Pernas
 * @email:  miguel.ramos.pernas@cern.ch
 *
 */

#include <stdio.h>

/// Display the input message
void display( char const* msg )
{
  fprintf(stdout, "%s", msg);
}

/// Display an error message
void error( char const* msg )
{
  fprintf(stderr, "%s", msg);
}
