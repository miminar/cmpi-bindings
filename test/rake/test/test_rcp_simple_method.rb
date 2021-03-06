#
# Testcase for root/cimv2:RCP_SimpleMethod
#
# Generated by 'genprovider' for use with cmpi-bindings-ruby
require 'rubygems'
require 'sfcc'
require 'test/unit'
require_relative "./helper"
$: << File.dirname(__FILE__)

class Test_RCP_SimpleMethod < Test::Unit::TestCase
  def setup
    @client, @op = Helper.setup 'RCP_SimpleMethod'
  end

  def teardown
    Helper.teardown
  end

  def test_registered
    cimclass = @client.get_class(@op)
    assert cimclass
    cimclass.each_property do |name, p|
      assert name
      assert p.state
      assert p.type
    end
  end

  def test_instance_names
    names = @client.instance_names(@op)
    assert names.size > 0
    names.each do |ref|
      ref.namespace = @op.namespace
      instance = @client.get_instance ref
      assert instance
      assert instance.Name
      if instance.Name
        assert_kind_of String, instance.Name # string
      end
      result = instance.ReturnTrue()
      assert result
      assert_equal true, result
    end
  end

end
