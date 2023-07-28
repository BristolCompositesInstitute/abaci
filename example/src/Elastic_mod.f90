!DIR$ FREEFORM
!>
!> Example Fortran module for reproducing linear elastic behaviour
!>
module Elastic_mod
use iso_fortran_env, only: dp=>real64
implicit none


!> Structure for encapsulating material properties by name
type elastic_props_t
  real(dp) :: e
  real(dp) :: xnu
end type elastic_props_t

contains


!> Top-level wrapper for linear elastic user material
subroutine umat_elastic(ddsdde, stress, props_array, dstran, ndi, nshr)
  real(dp), intent(out) :: ddsdde(:,:)
  real(dp), intent(inout) :: stress(:)
  real(dp), intent(in) :: props_array(:)
  real(dp), intent(in) :: dstran(:)
  integer, intent(in) :: ndi, nshr

  type(elastic_props_t) :: props

  props = get_properties(props_array)
  
  if (ndi==3 .and. nshr==1) then
    
    call plain_strain_jacobian(ddsdde, props)

  else if (ndi==2 .and. nshr==1) then
    
    call plain_stress_jacobian(ddsdde, props)

  else
    
    call jacobian_3d(ddsdde,props)

  end if

  call update_stress(stress, dstran, ddsdde)

end subroutine umat_elastic


!> Extract named material properties from props_array
function get_properties(props_array) result(props)
  real(dp), intent(in) :: props_array(:)
  type(elastic_props_t) :: props

  props%e = props_array(1)
  props%xnu = props_array(2)

end function get_properties


!> Calculate jacobian terms for plain strain or axisymmetric case
subroutine plain_strain_jacobian(ddsdde, props)
  real(dp), intent(out) :: ddsdde(:,:)
  type(elastic_props_t), intent(in) :: props

  ddsdde(:,:) = 0.d0

  ddsdde(1,1) = 1.d0 - props%xnu
  ddsdde(1,2) = props%xnu
  ddsdde(1,3) = props%xnu
  ddsdde(2,1) = props%xnu
  ddsdde(2,2) = 1.d0 - props%xnu
  ddsdde(2,3) = props%xnu
  ddsdde(3,1) = props%xnu
  ddsdde(3,2) = props%xnu
  ddsdde(3,3) = 1.d0 - props%xnu
  ddsdde(4,4) = 0.5d0*(1.d0 - 2.d0*props%xnu)

  ddsdde = ddsdde*props%e/( (1.d0 + props%xnu)*(1.d0-2.d0*props%xnu) )

end subroutine plain_strain_jacobian


!> Calculate jacobian terms for plains tress case
subroutine plain_stress_jacobian(ddsdde, props)
  real(dp), intent(out) :: ddsdde(:,:)
  type(elastic_props_t), intent(in) :: props

  ddsdde(:,:) = 0.d0

  ddsdde(1,1) = 1.d0
  ddsdde(1,2) = props%xnu
  ddsdde(2,1) = props%xnu
  ddsdde(2,2) = 1.d0
  ddsdde(3,3) = 0.5d0*(1.d0 - props%xnu)

  ddsdde = ddsdde*props%e/( (1.d0+props%xnu**2) )

end subroutine plain_stress_jacobian


!> Calculate jacobian terms for 3D case
subroutine jacobian_3d(ddsdde,props)
  real(dp), intent(out) :: ddsdde(:,:)
  type(elastic_props_t), intent(in) :: props

  ddsdde(:,:) = 0.d0

  ddsdde(1,1) = 1.d0-props%xnu
  ddsdde(1,2) = props%xnu
  ddsdde(1,3) = props%xnu
  ddsdde(2,1) = props%xnu
  ddsdde(2,2) = 1.d0-props%xnu
  ddsdde(2,3) = props%xnu
  ddsdde(3,1) = props%xnu
  ddsdde(3,2) = props%xnu
  ddsdde(3,3) = 1.d0-props%xnu
  ddsdde(4,4) = 0.5d0*(1.d0-2.d0*props%xnu)
  ddsdde(5,5) = ddsdde(4,4)
  ddsdde(6,6) = ddsdde(4,4)

  ddsdde = ddsdde*props%e/( (1.d0+props%xnu)*(1.d0-2.d0*props%xnu) )

end subroutine jacobian_3d


!> Update stress tensor from strain increments
subroutine update_stress(stress, dstran, ddsdde)
  real(dp), intent(inout) :: stress(:)
  real(dp), intent(in) :: dstran(:)
  real(dp), intent(in) :: ddsdde(:,:)

  integer :: i, j, ntens
  ntens = size(stress,1)

  do i = 1,ntens
    do j = 1,ntens
      stress(i) = stress(i) + ddsdde(i,j)*dstran(j)
    end do
  end do

end subroutine update_stress

end module Elastic_mod

!DIR$ NOFREEFORM
!DIR$ FIXEDFORMLINESIZE:132