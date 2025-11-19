import { useState } from 'react'
import { Input } from '@/components/common/Input'
import { Select } from '@/components/common/Select'
import { Checkbox } from '@/components/common/Checkbox'
import { Radio } from '@/components/common/Radio'
import { Card } from '@/components/common/Card'
import { Badge } from '@/components/common/Badge'
import { Avatar } from '@/components/common/Avatar'
import { Loader } from '@/components/common/Loader'
import { Skeleton } from '@/components/common/Skeleton'
import { Alert } from '@/components/common/Alert'
import { Button } from '@/components/common/Button'
import { Pagination } from '@/components/common/Pagination'
import { Tabs, Tab } from '@/components/common/Tabs'
import { Modal } from '@/components/common/Modal'
import { Tooltip } from '@/components/common/Tooltip'
import { useToast } from '@/hooks/useToast'

export default function ComponentsDemo() {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [currentPage, setCurrentPage] = useState(1)
  const [showAlert, setShowAlert] = useState(true)
  const { addToast } = useToast()

  const tabs: Tab[] = [
    {
      id: 'overview',
      label: 'Overview',
      content: (
        <div>
          <h3 className="text-lg font-semibold mb-2">Overview Tab</h3>
          <p className="text-gray-600">
            This is the overview tab content. Tabs allow you to organize content into separate views.
          </p>
        </div>
      ),
    },
    {
      id: 'details',
      label: 'Details',
      content: (
        <div>
          <h3 className="text-lg font-semibold mb-2">Details Tab</h3>
          <p className="text-gray-600">
            This is the details tab content with more specific information.
          </p>
        </div>
      ),
    },
    {
      id: 'settings',
      label: 'Settings',
      content: (
        <div>
          <h3 className="text-lg font-semibold mb-2">Settings Tab</h3>
          <p className="text-gray-600">
            Configure your settings here.
          </p>
        </div>
      ),
    },
  ]

  return (
    <div className="space-y-12 pb-12">
      <div>
        <h1 className="text-4xl font-bold text-gray-900 mb-2">UI Components Library</h1>
        <p className="text-lg text-gray-600">
          Comprehensive showcase of all reusable UI components in DEEO.AI
        </p>
      </div>

      {/* Input Components */}
      <section>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Input Components</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card>
            <h3 className="text-lg font-semibold mb-4">Text Input</h3>
            <div className="space-y-4">
              <Input
                label="Email"
                type="email"
                placeholder="email@example.com"
                helperText="We'll never share your email"
              />
              <Input
                label="Password"
                type="password"
                placeholder="••••••••"
                required
              />
              <Input
                label="Disabled Input"
                placeholder="Cannot edit"
                disabled
              />
              <Input
                label="Error State"
                placeholder="Invalid input"
                error="This field is required"
              />
            </div>
          </Card>

          <Card>
            <h3 className="text-lg font-semibold mb-4">Textarea & Select</h3>
            <div className="space-y-4">
              <Input
                label="Description"
                type="textarea"
                placeholder="Enter your message..."
                helperText="Maximum 500 characters"
              />
              <Select
                label="Country"
                options={[
                  { value: 'fr', label: 'France' },
                  { value: 'us', label: 'United States' },
                  { value: 'ma', label: 'Morocco' },
                  { value: 'uk', label: 'United Kingdom' },
                ]}
                helperText="Select your country"
              />
            </div>
          </Card>

          <Card>
            <h3 className="text-lg font-semibold mb-4">Checkbox</h3>
            <div className="space-y-3">
              <Checkbox label="Accept terms and conditions" />
              <Checkbox label="Subscribe to newsletter" />
              <Checkbox label="Remember me" defaultChecked />
              <Checkbox label="Disabled option" disabled />
            </div>
          </Card>

          <Card>
            <h3 className="text-lg font-semibold mb-4">Radio Buttons</h3>
            <div className="space-y-3">
              <Radio name="plan" label="Free plan" value="free" />
              <Radio name="plan" label="Pro plan" value="pro" defaultChecked />
              <Radio name="plan" label="Enterprise plan" value="enterprise" />
              <Radio name="plan" label="Disabled option" value="disabled" disabled />
            </div>
          </Card>
        </div>
      </section>

      {/* Display Components */}
      <section>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Display Components</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card>
            <h3 className="text-lg font-semibold mb-4">Badges</h3>
            <div className="space-y-4">
              <div className="flex flex-wrap gap-2">
                <Badge>Default</Badge>
                <Badge variant="primary">Primary</Badge>
                <Badge variant="success">Success</Badge>
                <Badge variant="warning">Warning</Badge>
                <Badge variant="error">Error</Badge>
                <Badge variant="info">Info</Badge>
              </div>
              <div className="flex flex-wrap gap-2">
                <Badge size="sm">Small</Badge>
                <Badge size="md">Medium</Badge>
                <Badge size="lg">Large</Badge>
              </div>
            </div>
          </Card>

          <Card>
            <h3 className="text-lg font-semibold mb-4">Avatars</h3>
            <div className="space-y-4">
              <div className="flex items-center gap-4">
                <Avatar alt="User" fallback="JD" size="sm" />
                <Avatar alt="User" fallback="AB" size="md" />
                <Avatar alt="User" fallback="CD" size="lg" />
                <Avatar alt="User" fallback="EF" size="xl" />
              </div>
              <div className="flex items-center gap-4">
                <Avatar alt="No fallback" size="md" />
                <Avatar alt="No fallback" size="lg" />
              </div>
            </div>
          </Card>

          <Card variant="bordered">
            <h3 className="text-lg font-semibold mb-2">Bordered Card</h3>
            <p className="text-gray-600">This card uses the bordered variant.</p>
          </Card>

          <Card variant="elevated">
            <h3 className="text-lg font-semibold mb-2">Elevated Card</h3>
            <p className="text-gray-600">This card uses the elevated variant with hover effect.</p>
          </Card>
        </div>
      </section>

      {/* Feedback Components */}
      <section>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Feedback Components</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card>
            <h3 className="text-lg font-semibold mb-4">Loaders</h3>
            <div className="space-y-4">
              <div className="flex items-center gap-4">
                <Loader size="sm" />
                <Loader size="md" />
                <Loader size="lg" />
              </div>
              <div className="flex items-center gap-4 bg-gray-800 p-4 rounded">
                <Loader size="md" color="white" />
                <Loader size="lg" color="white" />
              </div>
            </div>
          </Card>

          <Card>
            <h3 className="text-lg font-semibold mb-4">Skeleton Loading</h3>
            <div className="space-y-3">
              <Skeleton height="20px" />
              <Skeleton height="20px" width="80%" />
              <Skeleton height="20px" width="60%" />
              <div className="flex items-center gap-3 mt-4">
                <Skeleton variant="circular" width="40px" height="40px" />
                <div className="flex-1 space-y-2">
                  <Skeleton height="16px" />
                  <Skeleton height="16px" width="70%" />
                </div>
              </div>
            </div>
          </Card>

          <Card>
            <h3 className="text-lg font-semibold mb-4">Alerts</h3>
            <div className="space-y-3">
              <Alert variant="success" title="Success">
                Your changes have been saved successfully.
              </Alert>
              <Alert variant="warning">
                Please review your information before submitting.
              </Alert>
              <Alert variant="error" title="Error">
                An error occurred while processing your request.
              </Alert>
              {showAlert && (
                <Alert variant="info" onClose={() => setShowAlert(false)}>
                  This alert can be dismissed by clicking the X button.
                </Alert>
              )}
            </div>
          </Card>

          <Card>
            <h3 className="text-lg font-semibold mb-4">Toast Notifications</h3>
            <div className="space-y-3">
              <Button
                onClick={() => addToast({ message: 'Success! Operation completed.', type: 'success' })}
                variant="primary"
                className="w-full"
              >
                Show Success Toast
              </Button>
              <Button
                onClick={() => addToast({ message: 'Error! Something went wrong.', type: 'error' })}
                variant="primary"
                className="w-full"
              >
                Show Error Toast
              </Button>
              <Button
                onClick={() => addToast({ message: 'Info: This is an information message.', type: 'info' })}
                variant="primary"
                className="w-full"
              >
                Show Info Toast
              </Button>
              <Button
                onClick={() => addToast({ message: 'Warning! Please be careful.', type: 'warning' })}
                variant="primary"
                className="w-full"
              >
                Show Warning Toast
              </Button>
            </div>
          </Card>
        </div>
      </section>

      {/* Navigation Components */}
      <section>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Navigation Components</h2>
        <div className="grid grid-cols-1 gap-6">
          <Card>
            <h3 className="text-lg font-semibold mb-4">Pagination</h3>
            <div className="space-y-4">
              <p className="text-sm text-gray-600">Current page: {currentPage}</p>
              <Pagination
                currentPage={currentPage}
                totalPages={10}
                onPageChange={setCurrentPage}
              />
            </div>
          </Card>

          <Card>
            <h3 className="text-lg font-semibold mb-4">Tabs</h3>
            <Tabs tabs={tabs} />
          </Card>
        </div>
      </section>

      {/* Overlay Components */}
      <section>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Overlay Components</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card>
            <h3 className="text-lg font-semibold mb-4">Modal</h3>
            <div className="space-y-3">
              <Button onClick={() => setIsModalOpen(true)}>
                Open Modal
              </Button>
              <p className="text-sm text-gray-600">
                Click to open a modal dialog. Press ESC or click outside to close.
              </p>
            </div>
          </Card>

          <Card>
            <h3 className="text-lg font-semibold mb-4">Tooltip</h3>
            <div className="space-y-3">
              <div className="flex gap-4">
                <Tooltip content="This is a top tooltip" position="top">
                  <Button variant="ghost">Hover (Top)</Button>
                </Tooltip>
                <Tooltip content="This is a bottom tooltip" position="bottom">
                  <Button variant="ghost">Hover (Bottom)</Button>
                </Tooltip>
              </div>
              <div className="flex gap-4">
                <Tooltip content="This is a left tooltip" position="left">
                  <Button variant="ghost">Hover (Left)</Button>
                </Tooltip>
                <Tooltip content="This is a right tooltip" position="right">
                  <Button variant="ghost">Hover (Right)</Button>
                </Tooltip>
              </div>
            </div>
          </Card>
        </div>
      </section>

      {/* Button Variants (from existing components) */}
      <section>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Button Variants</h2>
        <Card>
          <div className="space-y-4">
            <div className="flex flex-wrap gap-3">
              <Button variant="primary">Primary</Button>
              <Button variant="secondary">Secondary</Button>
              <Button variant="ghost">Ghost</Button>
            </div>
            <div className="flex flex-wrap gap-3">
              <Button size="sm">Small</Button>
              <Button size="md">Medium</Button>
              <Button size="lg">Large</Button>
            </div>
            <div className="flex flex-wrap gap-3">
              <Button disabled>Disabled</Button>
              <Button variant="primary" disabled>Disabled Primary</Button>
            </div>
          </div>
        </Card>
      </section>

      {/* Modal Component */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Example Modal"
        size="md"
      >
        <div className="space-y-4">
          <p className="text-gray-600">
            This is an example modal dialog. You can put any content here.
          </p>
          <Input
            label="Name"
            placeholder="Enter your name"
          />
          <div className="flex justify-end gap-3">
            <Button variant="ghost" onClick={() => setIsModalOpen(false)}>
              Cancel
            </Button>
            <Button variant="primary" onClick={() => setIsModalOpen(false)}>
              Save
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
