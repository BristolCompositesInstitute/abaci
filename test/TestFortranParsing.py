import unittest
import tempfile
import os

from AbaciUnitTestSuite import AbaciUnitTestSuite

class TestFortranParsing(AbaciUnitTestSuite):

    def test_stmt_parsing(self):
        """Test statement parsing"""

        from abaci.fortran_parsing import parse_fortran_line

        def parse_check(line,parser,ident=None):

            parser1, ident1 = parse_fortran_line(line)
            self.assertEqual(parser1,parser)

            if ident:
                self.assertEqual(ident1[0].lower(),ident.lower())

        for stmt in ['subroutine asdf','subroutine asdf()',
                     'subroutine asdf (a)','subroutine asdf(a,b)',
                     'SUBROUTINE asdf()', ' SUBROUTINE ASDF()']:

            parse_check(stmt,'subroutine','asdf')

        for ident in ['a','z','A','Z','a1','a_1','long_subroutine_name']:

            parse_check('subroutine '+ident,'subroutine',ident)

        for stmt in ['module my_mod',' module my_mod','MODULE my_mod']:

            parse_check(stmt,'module','my_mod')


    def test_file_parsing(self):
        """
        Test that fortran parsing is correct
        """

        from abaci.fortran_parsing import parse_fortran_file

        fd,fort_file = tempfile.mkstemp()
        fh = os.fdopen(fd,'w')
        test_code = """
        module test_mod
            subroutine sub1
            end subroutine sub2
            subroutine sub2(a)
              integer, intent(in) :: a
            end subroutine sub2
            SUBROUTINE TEST_SUB
            END subroutine test_sub
            ! subroutine test_asdf()
            ! end subroutine test_asdf()
        end module test_mod

        subroutine lone_sub
        end subroutine lone_sub
        """

        fh.write(test_code)

        fh.close()

        mods = parse_fortran_file(fort_file)

        print mods
        
        self.assertIn('test_mod',mods)
        self.assertIn('subroutines',mods['test_mod'])
        self.assertIn('sub1',mods['test_mod']['subroutines'])
        self.assertIn('sub2',mods['test_mod']['subroutines'])
        self.assertIn('test_sub',mods['test_mod']['subroutines'])
        self.assertNotIn('test_asdf',mods['test_mod']['subroutines'])
        self.assertNotIn('lone_sub',mods['test_mod']['subroutines'])
        
        

