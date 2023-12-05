import * as algokit from '@algorandfoundation/algokit-utils'
import { useWallet } from '@txnlab/use-wallet'
import { useSnackbar } from 'notistack'
import { useEffect, useState } from 'react'
import { useAsyncRetry } from 'react-use'
import { ChainType, Duration, ProductState, SUBTOPIA_REGISTRY_ID, SubtopiaClient } from 'subtopia-js-sdk'
import { getAlgodConfigFromViteEnvironment } from '../utils/network/getAlgoClientConfigs'

interface DemoInterface {
  openModal: boolean
  setModalState: (value: boolean) => void
}

const DUMMY_SMI_ID = 481312144

const Demo = ({ openModal, setModalState }: DemoInterface) => {
  const [loading, setLoading] = useState<boolean>(false)

  const algodConfig = getAlgodConfigFromViteEnvironment()
  const algodClient = algokit.getAlgoClient({
    server: algodConfig.server,
    port: algodConfig.port,
    token: algodConfig.token,
  })

  const { enqueueSnackbar } = useSnackbar()
  const { signer, activeAddress } = useWallet()
  const [subtopiaClient, setSubtopiaClient] = useState<SubtopiaClient | null>()

  const subscriptionResponse = useAsyncRetry(async () => {
    if (!activeAddress || !subtopiaClient) {
      return undefined
    }

    return await subtopiaClient.getSubscription({
      algodClient: algodClient,
      subscriberAddress: activeAddress,
    })
  }, [activeAddress])

  const [subscriptionState, setSubscriptionState] = useState<ProductState | undefined>(undefined)

  const handleSubscribe = async () => {
    setLoading(true)

    if (!signer || !activeAddress || !subtopiaClient) {
      enqueueSnackbar('Please connect wallet first', { variant: 'warning' })
      return
    }

    try {
      enqueueSnackbar('Sending transaction...', { variant: 'info' })
      const response = await subtopiaClient
        .createSubscription({
          subscriber: {
            addr: activeAddress,
            signer: signer,
          },
          duration: Duration.MONTH,
        })
        .catch(() => {
          setLoading(false)
        })

      if (!response) {
        throw new Error('Failed to send transaction')
      }

      subscriptionResponse.retry()
      enqueueSnackbar(`Transaction sent: ${response.txID}`, { variant: 'success' })
    } catch (e) {
      enqueueSnackbar('Failed to send transaction', { variant: 'error' })
    }

    setLoading(false)
  }

  useEffect(() => {
    // async method to init and set subtopia
    const initSubtopiaClient = async () => {
      if (!activeAddress || !signer) {
        return
      }

      const client = await SubtopiaClient.init({
        algodClient: algodClient,
        productID: DUMMY_SMI_ID,
        chainType: ChainType.TESTNET,
        registryID: SUBTOPIA_REGISTRY_ID(ChainType.TESTNET),
        creator: {
          addr: activeAddress,
          signer: signer,
        },
      })

      const state = await client.getAppState()
      setSubscriptionState(state)
      setSubtopiaClient(client)
      subscriptionResponse.retry()
    }

    if (!subtopiaClient) {
      initSubtopiaClient()
    }
  })

  return (
    <dialog id="transact_modal" className={`modal ${openModal ? 'modal-open' : ''} bg-slate-200`}>
      <form method="dialog" className="modal-box">
        <h3 className="font-bold text-lg">Subscription status</h3>
        <br />
        {subscriptionState && (
          <>
            <p>{`Title: ${subscriptionState.productName} - ${subscriptionState.subscriptionName}`}</p>
            <p>{`Subscription type: ${subscriptionState.subType === 0 ? 'Unlimited' : 'Time Based'}`}</p>
            <p>{`Created at: ${new Date(subscriptionState.createdAt * 1000).toLocaleString('en-US', {
              month: 'short',
              day: 'numeric',
              year: 'numeric',
              hour: 'numeric',
              minute: 'numeric',
              timeZone: 'UTC',
            })}`}</p>
          </>
        )}
        <>
          <p>{subscriptionResponse.value ? `Status: Subscribed` : 'Status: Not subscribed'}</p>
        </>

        <div className="modal-action ">
          <button className="btn" onClick={() => setModalState(!openModal)}>
            Close
          </button>
          <button data-test-id="send-algo" className={`btn lo`} onClick={handleSubscribe}>
            {loading ? <span className="loading loading-spinner" /> : 'Subscribe'}
          </button>
        </div>
      </form>
    </dialog>
  )
}

export default Demo
